# NGP (Native Gadget Programming)
NGP and the NGP compiler are currently under development, and **this document addresses theoretical concepts only.**

Created by @therustymate

## Disclaimer

This document and all associated materials are provided strictly for **legitimate security research, education, and authorized antivirus detection capability testing purposes only.**  
The techniques and concepts described herein involve advanced software security, malware analysis, and development methods, and **any unauthorized use, reproduction, distribution, or malicious deployment against systems without explicit permission is strictly prohibited.**

By accessing and utilizing this material, you acknowledge and agree to comply with all applicable laws and regulations,  
and to obtain proper authorization before conducting any security testing or research activities.

The author and affiliated parties **expressly disclaim all legal liability and responsibility for any misuse, unauthorized actions, or damages arising from the use of this information.**

Furthermore, this research was conducted to study current antivirus detection limitations, develop evasion techniques for educational purposes, and enhance cybersecurity expertise.  
The disclosure of this technology is purely for advancing the security industry and academic research.

Therefore, all risks, legal responsibilities, and consequences resulting from the use or misuse of this document rest solely with the user.  
The author and related parties are fully indemnified from any direct or indirect damages.

By reading or using this document, you are deemed to have accepted all the above conditions.

## NGP Operation Principle

**NGP**, or **Native Gadget Programming**, is a novel technique designed to execute malicious code without embedding the actual shellcode within the shellcode dropper.  
This technology leverages byte fragments from binaries already present on the system to **reconstruct and execute shellcode in memory**, effectively evading antivirus detection.

---

## Operation Process

1. **Shellcode Analysis and Mapping** - The NGP compiler analyzes the provided shellcode and searches for **matching or similar byte sequences** within default Windows system files (e.g., executables, DLLs, other binary files).
2. **Fragment Location Storage** - When matching byte fragments are found, metadata such as **file path**, **file offset**, and **length** are recorded and hardcoded into the final dropper binary.
3. **Handling Missing Bytes** - If certain bytes cannot be found within system files, those fragments are stored in an **encrypted form in a specific section of the executable**.
4. **Dynamic Building at Runtime** - When the dropper executes, it opens the target files, reads the necessary byte fragments, decrypts encrypted fragments, and sequentially **rebuilds the shellcode in memory**.
5. **Shellcode Execution** - Finally, the reconstructed shellcode is loaded and executed in memory using APIs like `VirtualAlloc`, `memcpy`, `VirtualProtect`, or via ROP-like mechanisms.

---

Because the dropper does not contain fully executable shellcode but only incomplete fragment information,  
this approach is highly effective at evading signature-based antivirus detection.

Users can also partially evade detection of complete malicious binaries performing harmful actions via NGP.  
The NGP compiler analyzes the provided binary, maps portions to byte fragments within legitimate system files, and includes the rest in encrypted form in the dropper.  
At runtime, these fragments are reassembled in memory and loaded directly via techniques like Process Hollowing, effectively bypassing static antivirus analysis.

## Signature-Based Detection Evasion Mechanism

Signature-based detection identifies malware by matching unique byte patterns or code fragments stored in a database against files. This method achieves high detection rates when explicit malicious code fragments exist within a file.

However, NGP effectively evades signature detection for the following reasons:

* **Absence of Complete Malicious Code Patterns** – The dropper binary does not contain executable malicious bytes internally; instead, malicious code is fetched piecewise from external legitimate system files and reconstructed in memory, so no full malicious signature exists within the file.
* **Distributed and Reused Code Fragments** – Malicious code is fragmented and distributed in memory; these fragments exist identically or similarly within default Windows system files, reducing uniqueness and making detection difficult.
* **Use of Legitimate System File Code** – By reusing code fragments from legitimate files, antivirus products hesitate to classify these as malicious, lowering detection likelihood.

Consequently, NGP malware’s complete execution sequence is not present as a whole within a single file but dispersed and reassembled, making it difficult for traditional signature-based detection methods to effectively detect.

## YARA Rule Detection and NGP Evasion Potential

YARA is a tool that identifies malware based on specific patterns, strings, binary sequences, or regular expressions, widely used in static analysis and memory scanning. YARA rules typically include unique byte sequences, function signatures, and strings found in malware samples.

However, NGP is likely to evade YARA detection due to:

* **Distributed and Reassembled Malware Structure** – NGP splits malware into fragments that reference system binaries or are stored encrypted, reassembled only at runtime, meaning unique continuous byte patterns or strings do not exist within a single executable. This complicates YARA’s pattern matching.
* **Use of Legitimate System File Code** – Since malware fragments match bytes inside legitimate system files, writing YARA rules based on these fragments risks false positives and limits rule application.
* **Encryption and Encoding** – Some malware fragments are stored encrypted inside the dropper and decrypted only at runtime, preventing detection by static YARA rules.

Thus, NGP-based malware exhibits a high evasion rate against traditional YARA rules, requiring dynamic analysis or memory behavior-based detection techniques for effective identification.

## Major Differences and Implications Between Encrypted Shellcode and NGP

1. **Difficulty of Automated Full Content Analysis and Detection**  
* Encrypted shellcode exists wholly within the dropper in encrypted form; antivirus attempts to decrypt or analyze memory dumps at runtime.  
* NGP fragments malicious code across many legitimate system files, forcing antivirus to access and reconstruct fragments from numerous files, a complex and resource-intensive task.  
* This leads to overall system performance degradation during detection, undesirable for users or administrators.  
* For attackers, increased detection cost and resource consumption degrade defenders’ detection and response capabilities, enhancing attack success.

2. **Reduced Malware Size and Network Traffic**  
* NGP reuses code fragments from existing legitimate files, greatly reducing the pure size of malware to be delivered.  
* This compression-like effect reduces bandwidth and transmission time, lowering the chance of detection.  
* Less network traffic reduces suspicion by intrusion detection systems (IDS), favoring stealthy attacks.

3. **Enhanced Static Analysis and Signature Detection Evasion**  
* Encrypted shellcode is hard to detect before decryption, but NGP lacks a complete malicious signature in any single executable file, virtually neutralizing signature-based detection.  
* Fragmented malware spread over multiple legitimate files requires full assembly for detection, practically impossible without full context.

## Limitations and Constraints of NGP Technology

NGP offers strengths in evading static and signature-based detection but faces the following challenges:

1. **Difficulty of Complete Code Mapping**  
* Perfectly mapping all byte fragments inside legitimate Windows system files is practically impossible.  
* Some shellcode or malware bytes are absent or hard to find in system files, requiring encryption or separate storage.  
* This results in encrypted code sections inside the dropper, which may be subject to static or behavioral analysis.

2. **Limitations in Evading Memory-Based Detection (EDR)**  
* Runtime behaviors such as API calls, RWX (Read/Write/Execute) memory allocations, and code injections are monitored by modern EDR solutions.  
* System calls like `VirtualAlloc`, `WriteProcessMemory`, `CreateRemoteThread`, and `NtResumeThread` are vulnerable to behavioral detection.  
* While NGP can hide some activities using ROP techniques, **(EDR-evasive NGP is still under development)**, full evasion of dynamic detection remains difficult.

3. **Instability Due to Legitimate File Changes**  
* Updates or patches to system files change fragment offsets, causing assembly failures or malfunctions.  
* NGP is therefore version-dependent, complicating maintenance and response.

4. **Complex Development and Testing Environment**  
* Implementing NGP compilers and droppers requires complex integration of fragment mapping, encryption, decryption, and memory permission adjustments.  
* Improper implementation can degrade system stability and cause unexpected errors.

---

# Korean

## 면책 조항

본 문서 및 관련 자료는 **오직 보안 연구, 교육, 및 합법적인 안티바이러스 탐지 능력 테스트 목적으로만 제공**됩니다.  
여기서 설명하는 기술과 개념은 고급 소프트웨어 보안, 악성코드 분석 및 개발 기법을 포함하며, 이들은 **허가받지 않은 시스템에 대한 비인가된 사용, 복제, 배포 또는 악용을 엄격히 금지**합니다.

본 자료를 사용하는 모든 사용자는 관련 법률과 규정을 준수하고,  
모든 보안 테스트 및 연구 활동에 대해 **명확한 권한과 승인을 반드시 받아야 함**을 이해하고 동의하는 것으로 간주됩니다.  

저자 및 관련 단체는 본 자료의 부적절한 사용이나 불법 행위에 대해 **일체의 법적 책임을 지지 않으며, 어떠한 손해에 대해서도 책임을 부인합니다.**

또한, 본 연구는 **현재 안티바이러스 솔루션의 탐지 한계와 우회 기법 연구, 보안 전문가 교육, 그리고 보안 역량 강화**를 위해 수행된 것으로,  
본 기술의 공개는 보안 업계 및 학계의 발전을 위한 순수한 연구 목적임을 명확히 밝힙니다.

따라서 본 문서 및 연구 결과물 사용에 따른 모든 책임과 법적 문제는 전적으로 사용자 본인에게 있으며,  
저자와 관계자는 어떠한 직접적·간접적 피해에 대해서도 면책됨을 다시 한 번 명확히 합니다.

본 문서를 열람하거나 활용하는 즉시, 위 모든 조건에 동의하는 것으로 간주됩니다.

## NGP 작동 원리

**NGP**, 또는 **Native Gadget Programming**은 쉘코드 드랍퍼에 실제 쉘코드를 포함하지 않고도 악성 코드를 실행할 수 있도록 설계된 새로운 기법입니다.  
이 기술은 시스템에 이미 존재하는 바이너리 파일의 바이트 조각을 활용하여, **쉘코드를 메모리 내에서 재구성하고 실행**함으로써 백신 탐지를 회피할 수 있습니다.

---

## 작동 원리

1. **쉘코드 분석 및 매핑** - NGP 컴파일러는 사용자가 제공한 쉘코드를 분석한 뒤, Windows 시스템에 기본적으로 존재하는 파일들(예: 실행 파일, DLL, 기타 바이너리 포함 파일) 내부의 바이트 시퀀스와 **유사하거나 일치하는 조각들**을 찾아냅니다.
2. **조각 위치 저장** - 일치하는 바이트 조각이 발견되면 해당 조각의 **파일 경로**, **파일 내 오프셋**, **길이** 등의 정보를 메타데이터로 기록하고, 이 정보는 최종 드랍퍼 바이너리에 하드코딩됩니다.
3. **누락된 바이트 처리** - 만약 시스템 파일 내에서 찾을 수 없는 바이트가 있다면, 해당 바이트 조각은 **암호화된 형태로 실행 파일 내 특정 섹션에 저장**됩니다.
4. **실행 시점 동적 빌드** - 드랍퍼가 실행되면 하드코딩된 정보와 함께, 대상 파일들을 열어 필요한 바이트 조각을 읽어오고, 암호화된 조각은 복호화하여 메모리 상에 순차적으로 **쉘코드를 재조립**합니다.
5. **쉘코드 실행** - 최종적으로 `VirtualAlloc`, `memcpy`, `VirtualProtect` 등의 API 또는 ROP-like 메커니즘을 통해 재구성된 쉘코드를 메모리에 로드하고 실행합니다.

---

이 방식은 드랍퍼 내부에 실행 가능한 형태의 완전한 쉘코드가 아닌, 불완전한 조각 정보만 포함되기 때문에,
안티바이러스 시그니처 기반 탐지를 우회하는 데 매우 효과적입니다.

사용자는 단순한 쉘코드뿐만 아니라, 악성 행위를 수행하는 전체 악성코드 바이너리 또한 NGP 기술을 통해 부분적으로 탐지를 회피할 수 있습니다.
NGP 컴파일러는 사용자가 제공한 바이너리를 분석한 후, 그 일부를 시스템에 존재하는 정상 파일들의 바이트 조각으로 매핑하고, 나머지는 암호화된 형태로 드랍퍼에 포함합니다.
실행 시, 이 조각들을 메모리 상에서 재조립한 뒤, Process Hollowing 등의 기법을 활용해 악성 프로세스를 메모리 내에 직접 로드함으로써, 정적 분석 기반의 안티바이러스 탐지를 효과적으로 우회할 수 있습니다.

## 시그니처 기반 탐지 회피 메커니즘
시그니처 기반 탐지는 악성코드 내 고유한 바이트 패턴이나 코드 조각을 데이터베이스화하여, 파일 내 해당 패턴의 존재 여부를 검사하는 방식입니다. 이 방식은 파일에 악성 행위를 수행하는 명확한 코드 조각이 포함되어 있을 때 높은 탐지율을 보입니다.

그러나 NGP(Native Gadget Programming) 기술은 다음과 같은 이유로 시그니처 기반 탐지를 효과적으로 회피할 수 있습니다.
* 완전한 악성 코드 패턴의 부재 - 드랍퍼 바이너리 내부에 실행 가능한 악성 바이트가 포함되어 있지 않고, 악성 코드는 외부의 정상 시스템 파일로부터 조각 단위로 불러와 메모리 내에서 재구성되기 때문에, 탐지 대상이 되는 완성된 악성 시그니처가 파일 내에 존재하지 않습니다.
* 코드 조각의 분산 및 재활용 - 악성 코드가 메모리 내에서 여러 조각으로 분산되어 있고, 이 조각들은 Windows 시스템에 기본적으로 존재하는 정상 파일 내 바이트와 동일하거나 유사한 형태로 존재하기 때문에, 시그니처로서의 고유성이 낮고 탐지가 어려워집니다.
* 정상 시스템 파일 내 코드 활용 - 정상 파일 내에 존재하는 코드 조각을 재활용함으로써, 백신 프로그램이 일반적으로 정상 파일을 악성 시그니처로 등록하는 것을 꺼리게 되어 탐지 가능성이 낮아집니다.

결과적으로, NGP 기술은 악성 코드의 전체 실행 시퀀스가 단일 파일 내에 완전하게 존재하지 않고, 조각 단위로 분산 및 재조립되기 때문에 기존 시그니처 기반 탐지 방식으로는 효과적인 탐지가 어렵습니다.

## YARA 룰 탐지와 NGP 기술의 회피 가능성
YARA는 특정 패턴, 문자열, 바이너리 시퀀스 또는 정규식을 기반으로 악성코드를 식별하는 도구로, 정적 분석과 메모리 스캔에 널리 활용됩니다. 일반적으로 YARA 룰은 악성코드 샘플에서 발견되는 고유한 바이트 시퀀스, 함수 서명, 문자열 등을 포함하여 탐지를 수행합니다.

그러나 NGP(Native Gadget Programming) 기술은 다음과 같은 이유로 YARA 룰 탐지를 회피할 가능성이 높습니다.

* 악성 코드의 분산 및 재조립 구조 - NGP는 악성코드를 여러 조각으로 나누어 시스템에 존재하는 정상 바이너리에서 바이트를 참조하거나, 암호화된 형태로 저장하고 실행 시점에 메모리 내에서 재조립하기 때문에, 단일 실행 파일 내에 고유한 악성 패턴이 연속적으로 존재하지 않습니다. 이는 YARA 룰이 정의한 연속적인 바이트 패턴이나 문자열 매칭을 어렵게 만듭니다.
* 정상 시스템 파일 내 코드 활용 - 악성코드 조각이 정상 시스템 파일의 바이트 시퀀스와 동일하거나 유사한 형태로 존재하기 때문에, 해당 조각을 기준으로 YARA 룰을 작성하는 경우 정상 파일과 구분이 어렵습니다. 이로 인해 오탐(False Positive) 위험이 높아져 NGP를 대상으로하는 룰 적용에 제약이 따릅니다.
* 암호화 및 인코딩 기법 사용 - NGP는 드랍퍼 내에 악성 코드의 일부를 암호화하여 저장하며, 실행 시점에 복호화하여 메모리에 로드합니다. 이는 암호화된 상태에서는 YARA 룰로 탐지할 수 없게 하여 탐지 회피 효과를 높입니다.

따라서, NGP 기반 악성코드는 전통적인 YARA 룰 탐지에 대해 높은 회피율을 보이며, 이를 효과적으로 탐지하기 위해서는 동적 분석 또는 메모리 내 행위 기반 탐지 기법과의 결합이 요구됩니다.

## 암호화된 쉘코드와 NGP의 주요 차이점 및 의미
1. 전체 내용의 자동 분석 및 탐지 난이도 차이
* 암호화된 쉘코드는 드랍퍼 내에 암호화된 전체 코드가 존재하며, 악성코드를 탐지하려는 안티바이러스(AV)는 복호화를 시도하거나 실행 시점 메모리 덤프를 통해 코드를 분석해야 합니다.
* 반면 NGP는 악성 코드가 여러 조각으로 분산되어 시스템의 정상 파일 내에 숨겨져 있기 때문에, AV는 단일 파일이 아니라 대량의 시스템 파일들에 접근해 일일이 코드 조각을 찾아내고 조립해야 하는 복잡한 작업에 직면합니다.
* 이는 탐지 과정에서 시스템 전체 성능 저하와 리소스 과다 소모를 야기할 수 있으며, 이는 보통 사용자나 관리자 입장에서 바람직하지 않은 상황입니다.
* 공격자 입장에서는 이러한 탐지 비용 증가와 리소스 소모가 AV 업체나 기업 보안팀의 탐지/대응 역량을 저하시켜, 공격 성공률을 높이는 이점으로 작용합니다.

2. 악성코드 사이즈 감소 및 네트워크 트래픽 절감
* NGP는 악성코드의 상당 부분을 이미 존재하는 정상 파일에서 재활용함으로써, 전달해야 할 악성 코드의 순수 크기를 크게 줄일 수 있습니다.
* 이는 압축 효과와 유사하며, 공격자가 악성 페이로드를 전송할 때 필요한 대역폭과 시간, 그리고 탐지될 가능성을 모두 감소시킵니다.
* 네트워크 트래픽이 적다는 것은, 침입 탐지 시스템(IDS) 등에서 비정상 트래픽으로 의심받을 가능성을 낮추며, 은밀한 공격에 유리한 환경을 제공합니다.

3. 정적 분석 및 시그니처 기반 탐지 회피 강화
* 암호화된 쉘코드는 복호화 전에 탐지가 어려운 반면, NGP는 완성된 악성 코드 시그니처가 단일 실행 파일 내에 존재하지 않기 때문에, 시그니처 기반 탐지를 거의 무력화시킵니다.
* 조각화된 악성 코드가 여러 정상 파일에 분산되어 있고, 각 조각만으로는 악성 행위를 수행할 수 없으므로, 전체 코드를 조립하지 않는 한 탐지가 사실상 불가능합니다.

## NGP 기술의 한계 및 제약사항
NGP(Native Gadget Programming)는 정적 분석 및 시그니처 기반 탐지 회피에 강점을 가지지만, 다음과 같은 한계와 제약이 존재합니다.
1. 전체 코드 맵핑의 어려움
* Windows 시스템에 존재하는 정상 파일 내 모든 바이트 조각을 완벽히 매핑하는 것은 현실적으로 불가능합니다.
* 일부 쉘코드나 악성 코드 바이트는 정상 파일 내에서 찾기 어렵거나 존재하지 않아, 반드시 암호화 또는 별도 저장이 필요합니다.
* 이로 인해 드랍퍼 내부에 암호화된 코드 섹션이 존재하게 되어, 일부 정적 분석 및 행위 분석 대상이 될 수 있습니다.

2. 메모리 기반 탐지 (EDR) 회피 한계
* 동작 중인 프로세스 메모리 내에서 발생하는 API 호출, RWX(읽기/쓰기/실행) 권한 메모리 할당, 코드 주입 등의 행위는 최신 EDR 솔루션에서 모니터링 및 탐지 대상이 됩니다.
* 특히 VirtualAlloc, WriteProcessMemory, CreateRemoteThread, NtResumeThread 등 시스템 호출은 행위 기반 탐지에 취약할 수 있습니다.
* NGP는 ROP 기법 등으로 일부 행위를 은폐할 수 있으나 **(EDR 회피용 NGP는 아직 개발중에 있음)**, 완전한 동적 탐지 회피는 현재로서는 어렵습니다.

3. 정상 파일 변경에 따른 불안정성
* 정상 파일의 버전 변경, 업데이트, 패치 등으로 인해 코드 조각의 위치(오프셋)가 변경되면, 조각 재조립이 실패하거나 오동작할 수 있습니다.
* 따라서 NGP는 특정 OS/버전 및 파일 버전에 종속적인 한계가 있으며, 유지보수와 대응이 복잡합니다.

4. 복잡한 개발 및 테스트 환경 필요
* NGP 컴파일러 및 드랍퍼 구현은 복잡하며, 조각 매핑, 암호화, 복호화, 메모리 권한 조정 등 다양한 기술의 결합이 요구됩니다.
* 잘못된 구현 시 시스템 안정성 저하 및 예기치 못한 오류가 발생할 수 있습니다.
