# Aya MCP Hackathon: Building Standard Model Context Protocol Servers

Welcome to the first Aya MCP Hackathon! This guide will help you build servers that implement the **standard Model Context Protocol (MCP)**, allowing AI agents and applications to interact with your unique tools and data sources. You'll also learn how to register your server with the **Aya Hackathon Registry** so others can discover it during the event.

Note: This document mentions the Aya registry, which is not up yet.

## Goal

Build innovative services accessible via the **standard MCP protocol** and register them with our hackathon-specific **Aya Registry** for discovery.

## What is the *Standard* Model Context Protocol (MCP)?

MCP is an **open standard**, originally developed by Anthropic, designed to standardize communication between AI clients (like LLMs or autonomous agents) and external servers that provide tools or data context.

**Key Concepts of the Standard MCP:**

1.  **Client-Server Architecture:** An AI application (the *MCP Client*) connects to one or more *MCP Servers* that expose specific capabilities.
2.  **Communication Protocol:** MCP uses **JSON-RPC 2.0** for all messages. It is **not** a typical REST API where you define custom endpoints. Communication follows a structured request/response and notification pattern defined by the MCP specification.
3.  **Transports:** MCP defines how JSON-RPC messages are transported:
    * `stdio`: For communication between processes on the same machine (client and server communicate via standard input/output).
    * `HTTP+SSE` (Server-Sent Events): For remote communication over a network. The client connects via HTTP, and the server can push messages/events back over a persistent connection. *(For this hackathon, servers accessible via the Aya Registry will likely need to use the HTTP+SSE transport).*
4.  **Lifecycle & Core Methods:** MCP involves a specific interaction flow:
    * **Initialization:** Client and server perform a handshake (`initialize` request/response) to agree on capabilities and protocol details.
    * **Capability Discovery:** The server informs the client about the `Tools`, `Resources`, and `Prompts` it offers (e.g., via `workspace/didChangeCapabilities` notification).
    * **Interaction:** The client can then invoke `Tools` (e.g., using the `$/invoke` method) or request `Resources`.
5.  **Primitives:**
    * **Tools:** Functions the AI client can ask the server to execute (e.g., 'get_weather', 'send_email'). These often use JSON Schema to define input parameters and output formats.
    * **Resources:** Passive data sources the server provides context from (e.g., 'file_content', 'database_schema').
    * **Prompts:** Pre-defined interaction templates (less common focus initially).

**Crucially:** Building an MCP server means implementing a JSON-RPC 2.0 server that speaks the MCP dialect over a supported transport (likely HTTP+SSE for network accessibility).

**Learn More:** We strongly recommend reviewing the [Official Model Context Protocol Specification](https://modelcontextprotocol.io/) for detailed information.

## Hackathon Task: Build an MCP Server

Your primary goal is to create a server application that:

1.  Implements the **standard MCP protocol** (JSON-RPC over HTTP+SSE recommended).
2.  Responds correctly to standard MCP messages like `initialize`.
3.  Advertises at least one useful `Tool` or `Resource` capability.
4.  Implements the logic for your advertised capability(s).

## Aya Hackathon Registry & Discovery (*Hackathon-Specific*)

To allow participants to find and potentially interact with each other's servers *during this hackathon*, we are hosting the **Aya Registry**.

**Important:** This registry and its associated mechanisms (like registration and heartbeat) are **specific to this hackathon** and are **NOT** part of the standard MCP protocol itself.

### 1. Registering Your Server (Metadata Submission)

Once your MCP server is running and accessible (likely via HTTP+SSE), you need to tell our registry about it by submitting a JSON metadata file.

* **Process:** Add your submission as a JSON file (named uniquely, e.g., `your-service-name.json`) to the `submissions/20250503` directory via a pull request to this repository.
* **Schema:** Your JSON file must validate against the `submission_schema.json` provided in the repository. See the schema for detailed field requirements.
* **Key Metadata:** You'll provide information like:
    * Server name, provider details, contact info.
    * The **URI** where your MCP server can be reached via HTTP+SSE (e.g., `https://your-server.example.com/mcp`). Note: MCP over HTTP doesn't mandate a specific path, but `/mcp` is a potential convention.
    * Detailed descriptions of the `capabilities` (Tools/Resources) your *MCP server* offers, including their parameters (using JSON Schema is recommended, matching MCP standards).
    * Link to your server's source code repository.
    * Hackathon-specific tags or types (e.g., "Standard", "Crypto").

### 2. Optional Heartbeat (*Hackathon-Specific*) (*WIP: Server not up yet*)

To help keep the Aya Registry status up-to-date during the hackathon, you can *optionally* implement a heartbeat mechanism.

* **How:** Your server can send a simple HTTP POST request periodically (e.g., every 60 seconds) to a specific endpoint on the Aya Registry (URL to be provided: `https://mcpregistry.aya.cash/registry/v1/heartbeat/{your_server_id}`).
* **Purpose:** This simply signals to the *hackathon registry* that your server is still online. Failure to send heartbeats might temporarily de-list your server from the *hackathon's discovery UI*.
* **Reminder:** This heartbeat is **NOT** part of the standard MCP protocol.

## Implementation Guidance (Building the MCP Server)

1.  **Choose Language/Framework:** Select a language (Python, TypeScript, Node.js, Go, Rust, etc.) and find libraries that support implementing JSON-RPC 2.0 servers, ideally with support for HTTP+SSE transport.
2.  **Implement MCP Handshake:** Your server must handle the `initialize` request from an MCP client and respond correctly with its capabilities.
3.  **Define Capabilities:** Design the `Tools` or `Resources` your server will provide. Define their names, descriptions, input parameters (using JSON Schema), and output formats clearly.
4.  **Implement Capability Logic:** Write the code that executes when a client invokes your `Tool` (via `$/invoke`) or requests your `Resource`.
5.  **Advertise Capabilities:** Ensure your server correctly informs the client about its available capabilities after initialization (e.g., via `workspace/didChangeCapabilities` or in the `initialize` response).
6.  **Error Handling:** Implement proper JSON-RPC error responses as defined by the JSON-RPC 2.0 and MCP specifications.
7.  **Transport:** Set up your server to listen for connections using the chosen transport (recommend HTTP+SSE for discoverability in this hackathon).
8.  **Documentation:** Document your capabilities clearly within the capability definitions advertised by your server (this is standard MCP practice).
9.  **Testing:** Test your server using an MCP client or testing tool. We may provide simple client examples.

## Hackathon Submission Checklist

* [ ] MCP Server built implementing standard MCP (JSON-RPC, likely over HTTP+SSE).
* [ ] Server responds correctly to `initialize`.
* [ ] Server advertises at least one `Tool` or `Resource`.
* [ ] Server implements the logic for its capability(ies).
* [ ] Server handles MCP/JSON-RPC errors gracefully.
* [ ] (Recommended) Server is accessible over the internet via its HTTP+SSE endpoint.
* [ ] `submission.json` metadata file created and validated against `submission_schema.json`.
* [ ] (Optional) Implemented Aya Registry heartbeat mechanism.
* [ ] Pull Request submitted with your `submission.json` file.

## Best Practices & Security

* **HTTPS:** If using HTTP+SSE, always use HTTPS for secure communication. Ensure valid SSL certificates.
* **Authentication:** The MCP spec doesn't mandate a specific authentication method. For HTTP+SSE transports, consider standard web security practices like API keys (e.g., via headers) or other token-based methods if needed. Clearly document how clients should authenticate.
* **Rate Limiting:** Implement rate limiting on your server endpoint to prevent abuse.
* **Input Validation:** Validate parameters received in `$/invoke` requests rigorously.
* **Logging:** Implement robust logging within your server for debugging and monitoring.

## Submission Details & Validation

* Submit your server's metadata by adding a `your-service-name.json` file to the `submissions/20250503` directory via Pull Request.
* **Validate your JSON metadata file** before submitting:
    ```bash
    # Install validator dependency
    pip install jsonschema

    # Run the validator (from the repo root)
    python submission_validator.py submissions/20250503/your-service-name.json
    ```
* Ensure your JSON file accurately describes your *MCP server* and its capabilities.
* Remember the "Standard" vs. "Crypto" server types and requirements are specific to this hackathon's rules and prizes.

## Resources

* **Official MCP Specification:** [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)
* [Website](https://hackathon.aya.cash)
* Aya Registry API Details: *(Coming soon - You can skip for now)*
* Hackathon Telegram/Support Channel: [Aya Hackathon Telegram Channel](https://t.me/+SjnVESMxM3ZlOTQ6)

---

Happy building! We're excited to see the standard MCP servers you create and connect via the Aya Registry. If you have questions, please reach out on the support channel.
