import SwiftUI

struct StatusBar: View {
    @ObservedObject var vm: SearchViewModel

    var body: some View {
        HStack(spacing: 8) {
            if vm.isIngesting {
                ProgressView()
                    .controlSize(.small)
                    .scaleEffect(0.7)
            }

            if !vm.ingestProgress.isEmpty {
                Text(vm.ingestProgress)
                    .font(.system(size: 11))
                    .foregroundStyle(Color("TextMuted"))
            } else if !vm.results.isEmpty {
                Text("\(vm.results.count) result\(vm.results.count == 1 ? "" : "s")")
                    .font(.system(size: 11))
                    .foregroundStyle(Color("TextMuted"))
                    .monospacedDigit()
            }

            Spacer()

            if let error = vm.errorMessage {
                HStack(spacing: 4) {
                    Image(systemName: "exclamationmark.triangle")
                        .font(.system(size: 10))
                    Text(error)
                        .font(.system(size: 11))
                        .lineLimit(1)
                }
                .foregroundStyle(.orange)
            }

            if vm.watchedFolder != nil {
                HStack(spacing: 4) {
                    Circle()
                        .fill(vm.autoEmbedEnabled ? .green : Color("TextMuted"))
                        .frame(width: 5, height: 5)
                    Text(vm.autoEmbedEnabled ? "Watching" : "Watch paused")
                        .font(.system(size: 11))
                        .foregroundStyle(Color("TextMuted"))
                }
            }
        }
        .padding(.horizontal, 16)
        .frame(height: 28)
        .background(Color("Card"))
        .overlay(alignment: .top) {
            Divider().opacity(0.3)
        }
    }
}
