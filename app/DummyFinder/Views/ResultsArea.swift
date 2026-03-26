import SwiftUI

struct ResultsArea: View {
    @ObservedObject var vm: SearchViewModel

    var body: some View {
        Group {
            if vm.query.isEmpty {
                EmptyPrompt()
            } else if vm.results.isEmpty && !vm.isSearching {
                NoResults(query: vm.query)
            } else {
                ScrollView {
                    LazyVGrid(
                        columns: [GridItem(.adaptive(minimum: 240, maximum: 340), spacing: 10)],
                        spacing: 10
                    ) {
                        ForEach(vm.results) { result in
                            ResultCard(result: result)
                        }
                    }
                    .padding(16)
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

private struct EmptyPrompt: View {
    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: "sparkle.magnifyingglass")
                .font(.system(size: 36, weight: .ultraLight))
                .foregroundStyle(Color("TextMuted"))
            Text("Search images, PDFs, audio, video and text")
                .font(.system(size: 13, weight: .regular))
                .foregroundStyle(Color("TextMuted"))
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

private struct NoResults: View {
    let query: String

    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: "doc.questionmark")
                .font(.system(size: 30, weight: .ultraLight))
                .foregroundStyle(Color("TextMuted"))
            Text("No results for \"\(query)\"")
                .font(.system(size: 13))
                .foregroundStyle(Color("TextMuted"))
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

struct ResultCard: View {
    let result: SearchResult
    @State private var hovered = false

    var body: some View {
        Button {
            revealInFinder()
        } label: {
            VStack(alignment: .leading, spacing: 0) {
                // Top: category tag + score
                HStack {
                    CategoryTag(category: result.media_category)
                    Spacer()
                    Text("\(Int(result.similarity * 100))%")
                        .font(.system(size: 10, weight: .semibold, design: .rounded))
                        .foregroundStyle(Color("TextMuted"))
                        .monospacedDigit()
                }
                .padding(.horizontal, 12)
                .padding(.top, 12)
                .padding(.bottom, 8)

                // File name
                Text(result.file_name.isEmpty ? "Untitled" : result.file_name)
                    .font(.system(size: 13, weight: .medium))
                    .foregroundStyle(Color("TextPrimary"))
                    .lineLimit(1)
                    .truncationMode(.middle)
                    .padding(.horizontal, 12)

                // Preview
                if !result.preview.isEmpty {
                    Text(result.preview)
                        .font(.system(size: 11))
                        .foregroundStyle(Color("TextSecondary"))
                        .lineLimit(2)
                        .padding(.horizontal, 12)
                        .padding(.top, 4)
                }

                Spacer(minLength: 10)

                Divider().opacity(0.4)

                // File path at bottom
                HStack(spacing: 4) {
                    Image(systemName: "folder")
                        .font(.system(size: 9))
                        .foregroundStyle(Color("TextMuted"))
                    Text(result.file_path.isEmpty ? "—" : shortenPath(result.file_path))
                        .font(.system(size: 10))
                        .foregroundStyle(Color("TextMuted"))
                        .lineLimit(1)
                        .truncationMode(.head)
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
            }
            .frame(maxWidth: .infinity, minHeight: 110, alignment: .topLeading)
            .background(Color("Card"))
            .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: 10, style: .continuous)
                    .stroke(Color("Border"), lineWidth: 1)
            )
            .shadow(color: .black.opacity(hovered ? 0.08 : 0.03), radius: hovered ? 6 : 2, y: 2)
        }
        .buttonStyle(.plain)
        .onHover { hovered = $0 }
    }

    private func revealInFinder() {
        guard !result.file_path.isEmpty else { return }
        NSWorkspace.shared.selectFile(result.file_path, inFileViewerRootedAtPath: "")
    }

    private func shortenPath(_ path: String) -> String {
        path.replacingOccurrences(of: NSHomeDirectory(), with: "~")
    }
}

private struct CategoryTag: View {
    let category: String

    private var color: Color {
        switch category {
        case "image": return Color("TagImage")
        case "document": return Color("TagPDF")
        case "audio": return Color("TagAudio")
        case "video": return Color("TagVideo")
        case "text": return Color("TagText")
        default: return Color("TagDefault")
        }
    }

    private var icon: String {
        switch category {
        case "image": return "photo"
        case "document": return "doc.text"
        case "audio": return "waveform"
        case "video": return "film"
        case "text": return "doc.plaintext"
        default: return "doc"
        }
    }

    var body: some View {
        HStack(spacing: 3) {
            Image(systemName: icon)
                .font(.system(size: 9, weight: .semibold))
            Text(category.isEmpty ? "file" : category)
                .font(.system(size: 10, weight: .semibold))
        }
        .foregroundStyle(Color("TextSecondary"))
        .padding(.horizontal, 7)
        .padding(.vertical, 3)
        .background(color, in: Capsule())
    }
}
