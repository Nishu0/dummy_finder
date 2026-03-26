import SwiftUI

struct HeaderBar: View {
    @ObservedObject var vm: SearchViewModel

    var body: some View {
        HStack(spacing: 12) {
            Text("dummy finder")
                .font(.system(size: 13, weight: .semibold, design: .rounded))
                .foregroundStyle(Color("TextPrimary"))

            Spacer()

            FilterPills(vm: vm)

            Divider()
                .frame(height: 16)
                .opacity(0.4)

            FolderPickerButton(vm: vm)
        }
        .padding(.horizontal, 20)
        .frame(height: 44)
    }
}

private struct FilterPills: View {
    @ObservedObject var vm: SearchViewModel

    var body: some View {
        HStack(spacing: 4) {
            ForEach(vm.mediaTypes, id: \.self) { type in
                let selected = (vm.mediaFilter ?? "All") == type
                Button {
                    vm.mediaFilter = type == "All" ? nil : type
                } label: {
                    Text(type)
                        .font(.system(size: 11, weight: selected ? .semibold : .regular))
                        .foregroundStyle(selected ? Color("Accent") : Color("TextMuted"))
                        .padding(.horizontal, 8)
                        .padding(.vertical, 3)
                        .background(
                            selected ? Color("AccentSoft") : Color.clear,
                            in: Capsule()
                        )
                }
                .buttonStyle(.plain)
            }
        }
    }
}

private struct FolderPickerButton: View {
    @ObservedObject var vm: SearchViewModel

    var body: some View {
        HStack(spacing: 6) {
            Button {
                vm.pickFolder()
            } label: {
                Label(
                    vm.watchedFolder.map { URL(fileURLWithPath: $0).lastPathComponent } ?? "Watch folder",
                    systemImage: "folder"
                )
                .font(.system(size: 11, weight: .regular))
                .foregroundStyle(vm.watchedFolder != nil ? Color("Accent") : Color("TextMuted"))
                .lineLimit(1)
            }
            .buttonStyle(.plain)
            .help("Pick a folder to watch or index")

            if vm.watchedFolder != nil {
                Toggle("", isOn: Binding(
                    get: { vm.autoEmbedEnabled },
                    set: { _ in vm.toggleAutoEmbed() }
                ))
                .toggleStyle(.switch)
                .controlSize(.mini)
                .help(vm.autoEmbedEnabled ? "Auto-embed on" : "Auto-embed off")
            }
        }
    }
}
