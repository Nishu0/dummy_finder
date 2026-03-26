import Foundation

final class FolderWatcher {
    private var stream: FSEventStreamRef?
    private let path: String
    private let onChange: (String) -> Void

    init(path: String, onChange: @escaping (String) -> Void) {
        self.path = path
        self.onChange = onChange
    }

    func start() {
        let paths = [path] as CFArray
        let context = UnsafeMutablePointer<FolderWatcher>.allocate(capacity: 1)
        context.initialize(to: self)

        var ctx = FSEventStreamContext(
            version: 0,
            info: context,
            retain: nil,
            release: nil,
            copyDescription: nil
        )

        stream = FSEventStreamCreate(
            nil,
            { _, info, count, paths, _, _ in
                guard let info else { return }
                let watcher = Unmanaged<FolderWatcher>.fromOpaque(info).takeUnretainedValue()
                let pathsArray = unsafeBitCast(paths, to: NSArray.self)
                for i in 0 ..< count {
                    if let path = pathsArray[i] as? String {
                        watcher.onChange(path)
                    }
                }
            },
            &ctx,
            paths,
            FSEventStreamEventId(kFSEventStreamEventIdSinceNow),
            0.5,
            FSEventStreamCreateFlags(kFSEventStreamCreateFlagFileEvents | kFSEventStreamCreateFlagUseCFTypes)
        )

        if let stream {
            FSEventStreamScheduleWithRunLoop(stream, CFRunLoopGetMain(), CFRunLoopMode.defaultMode.rawValue)
            FSEventStreamStart(stream)
        }
    }

    func stop() {
        guard let stream else { return }
        FSEventStreamStop(stream)
        FSEventStreamInvalidate(stream)
        FSEventStreamRelease(stream)
        self.stream = nil
    }

    deinit { stop() }
}
