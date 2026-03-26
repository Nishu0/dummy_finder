import AppKit
import Combine
import Foundation

@MainActor
final class SearchViewModel: ObservableObject {
    @Published var query = ""
    @Published var results: [SearchResult] = []
    @Published var isSearching = false
    @Published var isIngesting = false
    @Published var ingestProgress: String = ""
    @Published var errorMessage: String? = nil
    @Published var watchedFolder: String? = nil
    @Published var autoEmbedEnabled = false
    @Published var mediaFilter: String? = nil

    private var debounceTask: Task<Void, Never>? = nil
    private var watcher: FolderWatcher? = nil

    let mediaTypes = ["All", "image", "audio", "video", "document", "text"]

    func onQueryChanged() {
        debounceTask?.cancel()
        guard !query.trimmingCharacters(in: .whitespaces).isEmpty else {
            results = []
            return
        }
        debounceTask = Task {
            try? await Task.sleep(nanoseconds: 300_000_000)
            guard !Task.isCancelled else { return }
            await performSearch()
        }
    }

    func performSearch() async {
        let trimmed = query.trimmingCharacters(in: .whitespaces)
        guard !trimmed.isEmpty else { return }
        isSearching = true
        errorMessage = nil
        do {
            let mt = (mediaFilter == "All" || mediaFilter == nil) ? nil : mediaFilter
            results = try await PythonBridge.shared.search(query: trimmed, limit: 12, mediaType: mt)
        } catch {
            errorMessage = error.localizedDescription
            results = []
        }
        isSearching = false
    }

    func pickFolder() {
        let panel = NSOpenPanel()
        panel.canChooseFiles = false
        panel.canChooseDirectories = true
        panel.allowsMultipleSelection = false
        panel.prompt = "Select Folder"
        if panel.runModal() == .OK, let url = panel.url {
            setWatchedFolder(url.path)
        }
    }

    func setWatchedFolder(_ path: String) {
        watchedFolder = path
        if autoEmbedEnabled {
            startWatcher(path: path)
        }
    }

    func toggleAutoEmbed() {
        autoEmbedEnabled.toggle()
        if autoEmbedEnabled, let path = watchedFolder {
            startWatcher(path: path)
            Task { await ingestFolder(path: path) }
        } else {
            stopWatcher()
        }
    }

    private func startWatcher(path: String) {
        stopWatcher()
        watcher = FolderWatcher(path: path) { [weak self] changedPath in
            Task { @MainActor [weak self] in
                await self?.handleFileChange(path: changedPath)
            }
        }
        watcher?.start()
    }

    private func stopWatcher() {
        watcher?.stop()
        watcher = nil
    }

    private func handleFileChange(path: String) async {
        let url = URL(fileURLWithPath: path)
        guard !path.lastPathComponent.hasPrefix(".") else { return }
        guard FileManager.default.fileExists(atPath: path) else { return }
        ingestProgress = "Embedding \(url.lastPathComponent)..."
        do {
            _ = try await PythonBridge.shared.ingestFile(path: path)
        } catch {
            // Silently skip unsupported files from watcher
        }
        ingestProgress = ""
    }

    func ingestFolder(path: String) async {
        isIngesting = true
        ingestProgress = "Scanning \(URL(fileURLWithPath: path).lastPathComponent)..."
        do {
            let results = try await PythonBridge.shared.ingestDirectory(path: path)
            let embedded = results.filter { $0.status == "embedded" }.count
            let skipped = results.filter { $0.status == "skipped" }.count
            ingestProgress = "Done — \(embedded) embedded, \(skipped) skipped"
        } catch {
            ingestProgress = "Error: \(error.localizedDescription)"
        }
        isIngesting = false
        try? await Task.sleep(nanoseconds: 3_000_000_000)
        ingestProgress = ""
    }
}

private extension String {
    var lastPathComponent: String {
        URL(fileURLWithPath: self).lastPathComponent
    }
}
