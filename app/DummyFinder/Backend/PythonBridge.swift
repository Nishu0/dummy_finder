import Foundation

enum BridgeError: LocalizedError {
    case pythonNotFound
    case executionFailed(String)
    case decodingFailed(String)

    var errorDescription: String? {
        switch self {
        case .pythonNotFound: return "Python 3 not found. Make sure it is installed."
        case .executionFailed(let msg): return "Command failed: \(msg)"
        case .decodingFailed(let msg): return "Could not decode response: \(msg)"
        }
    }
}

actor PythonBridge {
    static let shared = PythonBridge()

    private let projectRoot: String
    private let python: String

    init() {
        let fileURL = URL(fileURLWithPath: #file)
        let root = fileURL
            .deletingLastPathComponent()
            .deletingLastPathComponent()
            .deletingLastPathComponent()
            .deletingLastPathComponent()
            .path
        self.projectRoot = root
        self.python = Self.resolvePython(root: root)
    }

    private static func resolvePython(root: String) -> String {
        let candidates = [
            "\(root)/.venv/bin/python3",
            "\(root)/venv/bin/python3",
            "/usr/local/bin/python3",
            "/usr/bin/python3",
        ]
        return candidates.first { FileManager.default.fileExists(atPath: $0) } ?? "python3"
    }

    func run(args: [String]) async throws -> String {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: python)
        process.arguments = ["-m", "dummy_finder.cli"] + args
        process.currentDirectoryURL = URL(fileURLWithPath: projectRoot)

        var env = ProcessInfo.processInfo.environment
        env["PYTHONPATH"] = projectRoot
        process.environment = env

        let stdout = Pipe()
        let stderr = Pipe()
        process.standardOutput = stdout
        process.standardError = stderr

        try process.run()
        process.waitUntilExit()

        let output = String(data: stdout.fileHandleForReading.readDataToEndOfFile(), encoding: .utf8) ?? ""
        let errOutput = String(data: stderr.fileHandleForReading.readDataToEndOfFile(), encoding: .utf8) ?? ""

        if process.terminationStatus != 0 {
            throw BridgeError.executionFailed(errOutput.isEmpty ? output : errOutput)
        }
        return output
    }

    func search(query: String, limit: Int = 10, mediaType: String? = nil) async throws -> [SearchResult] {
        var args = ["search", query, "--limit", "\(limit)", "--json"]
        if let mt = mediaType, !mt.isEmpty {
            args += ["--media-type", mt]
        }
        let raw = try await run(args: args)
        guard let data = raw.data(using: .utf8) else {
            throw BridgeError.decodingFailed("Empty output")
        }
        do {
            return try JSONDecoder().decode([SearchResult].self, from: data)
        } catch {
            throw BridgeError.decodingFailed(error.localizedDescription)
        }
    }

    func ingestFile(path: String, description: String = "") async throws -> IngestResult {
        var args = ["ingest-file", path]
        if !description.isEmpty { args += ["--description", description] }
        let raw = try await run(args: args)
        guard let data = raw.data(using: .utf8) else {
            throw BridgeError.decodingFailed("Empty output")
        }
        return try JSONDecoder().decode(IngestResult.self, from: data)
    }

    func ingestDirectory(path: String, recursive: Bool = true) async throws -> [IngestResult] {
        var args = ["ingest-dir", path]
        if recursive { args.append("--recursive") }
        let raw = try await run(args: args)
        guard let data = raw.data(using: .utf8) else {
            throw BridgeError.decodingFailed("Empty output")
        }
        return try JSONDecoder().decode([IngestResult].self, from: data)
    }
}
