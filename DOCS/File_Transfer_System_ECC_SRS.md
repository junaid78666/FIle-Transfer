RGUKT RK VALLEY | SOFTWARE REQUIREMENTS SPECIFICATION

## RGUKT RK VALLEY

## Department of Computer Science and Engineering

## SOFTWARE REQUIREMENTS SPECIFICATION

## File Transfer System Using Elliptic Curve Cryptography

## Department : Computer Science and Engineering Student Name : Sk.Md.Junaid ID Number : R220424 Roll No:58 Academic Year : 2026–2027


## RGUKT RK VALLEY | SOFTWARE REQUIREMENTS SPECIFICATION

## Document Information

| Item Details |
| --- |
| Document Type Software Requirements Specification (SRS) |
| Version 1.0 |
| Status Initial version |
| Project File Transfer System Using Elliptic Curve Cryptography |

## Version History

| Version | Date | Prepared By | Description |
| --- | --- | --- | --- |
| 1.0 | September 2026 | Sk.Md.Junaid | Initial draft of the Software Requirements Specification. |

## Table of Contents

1. Introduction ............................................................................................... 3

2. Overall Description ............................................................................................... 3

3. System Overview ............................................................................................... 4

4. Functional Requirements ............................................................................................... 6

5. Use-Case Overview ............................................................................................... 7

6. External Interface Requirements ............................................................................................... 9

7. Non-Functional Requirements ............................................................................................... 9

8. Security Requirements ............................................................................................... 10

9. Constraints and Assumptions ............................................................................................... 10

10. Conclusion ............................................................................................... 10


## RGUKT RK VALLEY | SOFTWARE REQUIREMENTS SPECIFICATION

## 1. Introduction

## 1.1 Purpose

This Software Requirements Specification defines the requirements for the File Transfer System Using Elliptic Curve Cryptography (ECC). The system is intended to provide secure file sharing between authenticated users by combining public-key cryptography with symmetric encryption.

## 1.2 Scope

The system provides a web-based mechanism for securely transferring documents, images, PDFs, text files, ZIP archives, and other digital files between authenticated users. ECC is used for secure key establishment or protection of a session key, while AES is used to encrypt the actual file efficiently. The initial implementation can be deployed on a local network or server.

The project can later be extended with cloud storage, multiple recipients, digital signatures, two-factor authentication, expiring download links, and mobile support.

## 1.3 Intended Users

The system is designed for authenticated users who need to send and receive files securely. The project is also intended to demonstrate practical application of cryptography, secure networking, Python web development, and database technologies.

## 1.4 Definitions and Acronyms

| Term Meaning |
| --- |
| ECC Elliptic Curve Cryptography |
| AES Advanced Encryption Standard |
| SHA-256 Secure Hash Algorithm with 256-bit output |
| SRS Software Requirements Specification |
| Session Key Temporary symmetric key used to encrypt file data |

## 1.5 References

- The project overview document supplied for the File Transfer System Using Elliptic Curve Cryptography.

- The reference SRS format supplied for Secure Data Transfer Over Internet Using Image Steganography.

## 2. Overall Description

## 2.1 Product Perspective

The proposed product is a web-based secure file-transfer application consisting of a user interface, backend processing, cryptographic components, database/storage, and network communication. Registered users authenticate themselves before using protected transfer functions.

## 2.2 Main Product Functions

- User registration and authentication.

- ECC public/private key generation.

- Secure key exchange or session-key protection.

- AES-based file encryption.

- Encrypted file transfer.

- File decryption by the authorized recipient.

- Integrity verification.

- Secure file download.

- Transfer history.


## RGUKT RK VALLEY | SOFTWARE REQUIREMENTS SPECIFICATION

## 2. Overall Description (continued)

## 2.3 User Characteristics

Users are expected to have basic computer or smartphone skills, including logging in, selecting files, uploading or downloading data, and using a web application. No specialist cryptography knowledge is required for normal use.

## 2.4 Operating Environment

- Web application accessible through a modern web browser.

- Server capable of running the selected Python backend framework and cryptographic libraries.

- Database such as SQLite or MySQL for application data.

- Network connection for transferring encrypted files between users.

## 2.5 Assumptions and Dependencies

- Users have access to the application and a functioning network connection.

- Registered users have valid credentials.

- The receiver has the appropriate ECC private key required for key recovery.

- Cryptographic keys are protected from unauthorized access.

- The server and database remain available during a transfer.

## 3. System Overview

## 3.1 System Workflow

The system follows a sender-to-receiver workflow. Authentication is performed before protected operations. A random AES session key is generated for file encryption, while ECC is used to establish a shared secret or securely protect the AES session key. The encrypted file and required cryptographic information are transferred to the recipient. The receiver recovers the session key, decrypts the file, verifies integrity, and accesses the original file.

| Stage | System Operation |
| --- | --- |
| 1 | Sender authenticates and selects a file. |
| 2 | System generates an AES session key. |
| 3 | File is encrypted using AES. |
| 4 | ECC key pair/key agreement protects or establishes the AES session key. |
| 5 | Encrypted file and protected key information are transferred. |
| 6 | Receiver authenticates and recovers the AES session key using ECC. |
| 7 | Receiver decrypts the file using AES. |
| 8 | System verifies file integrity and permits authorized download. |


RGUKT RK VALLEY | SOFTWARE REQUIREMENTS SPECIFICATION

*Figure: Simplified secure file-transfer workflow*

## 3.2 System Context

| Sender | Secure File Transfer System | Receiver |
| --- | --- | --- |
| Authenticate, select, encrypt | Key management, transfer, storage, validation | Authenticate, recover key, decrypt, download |
| Send encrypted data | Network communication | Receive encrypted data |


## RGUKT RK VALLEY | SOFTWARE REQUIREMENTS SPECIFICATION

## 3. System Overview (continued)

## 3.3 System Architecture / Flow Chart

The original project document contains the system flow chart showing authentication, ECC key generation/recovery, AES session-key generation, encryption/decryption, integrity verification, and authorized

download.

## 3.4 Actors and Events

| Actor | Responsibilities |
| --- | --- |
| Sender | Registers/logs in, selects a file, initiates secure transfer, and sends the encrypted data to the intended recipient. |
| Receiver | Logs in, receives the encrypted file, recovers the session key, decrypts the file, verifies it, and downloads it. |
| System/Server | Authenticates users, generates/manages cryptographic keys, encrypts/decrypts, transfers/stores data, and performs integrity verification. |

## Key Events

| # | Actor | Event | System Response |
| --- | --- | --- | --- |
| 1 | Sender | Logs in and selects file | Authenticates user and prepares transfer |
| 2 | Sender | Initiates transfer | Generates AES session key and encrypts file |
| 3 | System | Protects session key | Uses ECC key operations for secure key establishment/protection |
| 4 | Receiver | Receives encrypted transfer | Validates recipient access |
| 5 | Receiver | Requests file recovery | Recovers AES session key and decrypts file |
| 6 | System | Completes verification | Allows download if integrity is valid; otherwise rejects |


## RGUKT RK VALLEY | SOFTWARE REQUIREMENTS SPECIFICATION

## 4. Functional Requirements

## 4.1 Authentication Requirements

| ID | Requirement |
| --- | --- |
| FR-01 | The system shall allow users to register an account. |
| FR-02 | The system shall authenticate registered users before protected functions are accessed. |
| FR-03 | The system shall provide access control for protected file-transfer operations. |

## 4.2 Sender Requirements

| ID | Requirement |
| --- | --- |
| FR-04 | The system shall allow the sender to select a file for transfer. |
| FR-05 | The system shall generate an ECC public/private key pair for users as required by the key-management process. |
| FR-06 | The system shall generate a random AES session key for file encryption. |
| FR-07 | The system shall encrypt the selected file using AES before transmission. |
| FR-08 | The system shall use ECC for secure key establishment or protection of the AES session key. |
| FR-09 | The system shall transfer the encrypted file and required protected key information to the intended recipient. |

## 4.3 Receiver Requirements

| ID | Requirement |
| --- | --- |
| FR-10 | The system shall allow the intended receiver to access the transferred encrypted file. |
| FR-11 | The system shall use the receiver's appropriate ECC private-key operation for session-key recovery. |
| FR-12 | The system shall decrypt the transferred file using the recovered AES session key. |
| FR-13 | The system shall verify the integrity of the received file. |
| FR-14 | The system shall allow the receiver to download the original file after successful verification. |
| FR-15 | The system shall deny access to unauthorized recipients. |

## 4.4 Transfer Management Requirements

- The system shall maintain relevant information about previous transfers as transfer history.

- The system shall protect cryptographic key information during transfer and storage.

- The system shall report failed operations without presenting an invalid transfer as successful.


## RGUKT RK VALLEY | SOFTWARE REQUIREMENTS SPECIFICATION

## 5. Use-Case Overview

## 5.1 Use-Case Diagram

| Actor | Use Case | Description |
| --- | --- | --- |
| Sender | Register / Login | Create an account or authenticate before protected operations. |
| Sender | Select File | Choose the file to be securely transferred. |
| Sender | Create Secure Transfer | Generate AES key, encrypt file, protect session key using ECC, and transfer data. |
| Receiver | Login | Authenticate as a registered user. |
| Receiver | Receive Transfer | Obtain the encrypted file and protected key information. |
| Receiver | Recover and Decrypt | Recover the AES key using ECC and decrypt the file. |
| Receiver | Verify and Download | Verify integrity and download the original file. |

## 5.2 Use-Case List

| Use Case | Primary Actor | Description |
| --- | --- | --- |
| Create Secure Transfer | Sender | Encrypts a selected file using AES and securely protects/establishes its session key using ECC. |
| Receive Transfer | Receiver | Receives the encrypted file and associated protected key information. |
| Recover File | Receiver | Recovers the AES session key, decrypts the file, verifies integrity, and downloads the original. |

## 5.3 Detailed Use-Case: Create Secure Transfer

| Field | Details |
| --- | --- |
| Use-Case ID | UC-01 |
| Use-Case Name | Create Secure Transfer |
| Primary Actor | Sender |
| Description | The sender selects a file and creates a secure transfer using AES encryption and ECC-based key management. |
| Precondition | The sender is registered/authenticated and has a file to transfer. |
| Main Flow | 1. Sender logs in. 2. Selects file. 3. System generates AES session key. 4. File is encrypted using AES. 5. ECC protects/establishes the session key. 6. Encrypted data is transferred to the intended receiver. |
| Alternative Flow | If authentication, encryption, key management, or transfer fails, the system reports an error and does not present the operation as successful. |
| Postcondition | An encrypted file transfer is created for the intended recipient. |


## RGUKT RK VALLEY | SOFTWARE REQUIREMENTS SPECIFICATION

## 5. Use-Case Overview (continued)

## 5.4 Detailed Use-Case: Receive Transfer

| Field | Details |
| --- | --- |
| Use-Case ID | UC-02 |
| Use-Case Name | Receive Transfer |
| Primary Actor | Receiver |
| Description | The receiver authenticates and obtains the encrypted file and the required protected key information. |
| Precondition | The receiver is registered/authenticated and is an intended recipient. |
| Main Flow | 1. Receiver logs in. 2. System validates access. 3. Receiver receives the encrypted transfer. 4. Protected key information is made available for recovery. |
| Alternative Flow | If the receiver is unauthorized or the transfer is unavailable, access is denied and an error is displayed. |
| Postcondition | The encrypted file is available for recovery and decryption. |

## 5.5 Detailed Use-Case: Recover File

| Field | Details |
| --- | --- |
| Use-Case ID | UC-03 |
| Use-Case Name | Recover File |
| Primary Actor | Receiver |
| Description | The receiver recovers the AES session key using ECC, decrypts the file, verifies integrity, and downloads the original file. |
| Precondition | The receiver has authorized access to the encrypted transfer and the appropriate ECC private key. |
| Main Flow | 1. Receiver requests recovery. 2. System performs ECC key recovery. 3. AES session key is recovered. 4. File is decrypted using AES. 5. Integrity is verified. 6. Original file is made available for download. |
| Alternative Flow | If key recovery, decryption, or integrity verification fails, the system rejects the operation and displays an error. |
| Postcondition | The receiver downloads the verified original file. |

## 6. External Interface Requirements

## 6.1 User Interface

- The interface shall provide registration and login controls.

- The interface shall provide a file-selection control for the sender.

- The interface shall display transfer and processing status.

- The interface shall provide clear success and error notifications.

- The interface should be usable on common desktop and mobile-sized screens.

## 6.2 Input Interfaces

- User registration/login credentials.

- File selected by the sender.

- Recipient/transfer information as required by the implementation.

- Cryptographic key information managed by the application.


## RGUKT RK VALLEY | SOFTWARE REQUIREMENTS SPECIFICATION

## 6. External Interface Requirements (continued)

## 6.3 Output Interfaces

- Encrypted file/transfer status.

- Success and error messages.

- Decrypted original file available for authorized download.

- Transfer history information.

## 6.4 Software Interfaces

The application may use a Python web backend, Flask web framework, HTML5, CSS3, JavaScript, a cryptographic library for ECC and AES operations, and SQLite or MySQL for database management. Git/GitHub may be used for version control.

## 7. Non-Functional Requirements

| Category | Requirement |
| --- | --- |
| Security | Files shall be encrypted before transmission. ECC shall be used for secure key establishment or session-key protection. |
| Usability | The system shall provide a simple workflow and understandable instructions for authenticated users. |
| Performance | The system should perform encryption, transfer, decryption, and download within a reasonable time for supported file sizes. |
| Reliability | The system shall report failed operations without producing an apparently successful but unusable transfer. |
| Availability | The application shall be available when required, subject to server and network availability. |
| Compatibility | The web application should work with commonly used modern browsers. |
| Maintainability | The system should be organized into separate authentication, processing, cryptographic, storage, and interface components. |

## Technologies Used

| Technology | Purpose |
| --- | --- |
| Python | Backend programming |
| Flask | Web application framework |
| HTML5 | Web page structure |
| CSS3 | User interface styling |
| JavaScript | Client-side functionality |
| ECC | Secure key establishment / key protection |
| AES | Efficient file encryption |
| SHA-256 / authenticated encryption | Integrity and authenticity support |
| SQLite / MySQL | Database management |
| Git / GitHub | Version control |


## RGUKT RK VALLEY | SOFTWARE REQUIREMENTS SPECIFICATION

## 8. Security Requirements

- The system shall encrypt files before transmission.

- The system shall use ECC for secure public-key operations and session-key management.

- Private keys shall be protected from unauthorized access.

- The system shall verify the integrity of transferred data.

- The system shall provide authentication and access control.

- The system shall deny unauthorized recipients access to protected files.

- Cryptographic information shall not be unnecessarily exposed through application messages or transfer metadata.

- Secure communication such as HTTPS should be used when deployed for actual Internet use.

## 9. Constraints and Assumptions

| Type | Description |
| --- | --- |
| Constraint | Encryption and decryption introduce processing overhead. |
| Constraint | Private-key protection and key management must be implemented correctly. |
| Constraint | Network connectivity is required for remote transfer. |
| Constraint | Very large files may require additional storage and processing resources. |
| Constraint | Overall security depends on correct implementation and secure configuration. |
| Assumption | The receiver can recover the original file only when the required authorization and cryptographic key information are available. |

## 10. Conclusion

This SRS defines the essential requirements for a web-based File Transfer System Using Elliptic Curve Cryptography. By combining ECC for secure key management with AES for efficient file encryption, the system provides a practical approach to confidentiality, secure key handling, integrity verification, authentication, and access control. The requirements in this document can serve as the basis for design, implementation, testing, and evaluation of the project.
