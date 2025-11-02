# Tsuki

## Overview
Tsuki is a messaging software built with **privacy** and **simplicity** in mind.  

Our philosophy is to keep the codebase **small**, **secure**, and **lightweight**, without any unnecessary complexity or bloat.  
Tsuki is designed for people who actually **need** privacy — not marketing buzzwords.

---

## Philosophy
- Minimal and readable codebase  
- Security through simplicity  
- No unnecessary abstractions or frameworks  
- Easy to audit and maintain  
- Lightweight and efficient — built to do one thing well

---

##  Backend Roadmap

### Core Features
- [ ] **WebSocket Server**  
  - Lightweight async event loop (`asyncio` + `websockets`)  
  - Minimal routing for connections and messaging  

- [ ] **User Key Handshake**  
  - Generate ephemeral or persistent key pairs (`PyNaCl`)  
  - Exchange public keys securely during connection handshake  
  - Encrypted channel per session  

- [ ] **Point-to-Point User Messaging**  
  - End-to-end encrypted message passing  
  - Stateless server (no message storage)  
  - With binary payloads using `CBOR` 

- [ ] **Access Key for Private Servers**  
  - Optional access key or token required to connect  
  - Simple ACL for restricting unauthorized users  

---


