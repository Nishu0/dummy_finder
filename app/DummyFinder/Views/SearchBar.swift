import SwiftUI

struct SearchBar: View {
    @ObservedObject var vm: SearchViewModel
    @FocusState private var focused: Bool

    var body: some View {
        HStack(spacing: 10) {
            Image(systemName: "magnifyingglass")
                .font(.system(size: 15, weight: .light))
                .foregroundStyle(Color("TextMuted"))

            TextField("Search your files…", text: $vm.query)
                .font(.system(size: 16, weight: .light))
                .textFieldStyle(.plain)
                .foregroundStyle(Color("TextPrimary"))
                .focused($focused)
                .onAppear { focused = true }

            if vm.isSearching {
                ProgressView()
                    .controlSize(.small)
                    .scaleEffect(0.8)
            } else if !vm.query.isEmpty {
                Button {
                    vm.query = ""
                    vm.results = []
                } label: {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundStyle(Color("TextMuted"))
                }
                .buttonStyle(.plain)
            }
        }
        .padding(.horizontal, 20)
        .frame(height: 52)
    }
}
