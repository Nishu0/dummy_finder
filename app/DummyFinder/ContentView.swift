import SwiftUI

struct ContentView: View {
    @StateObject private var vm = SearchViewModel()

    var body: some View {
        ZStack {
            Color("Surface")
                .ignoresSafeArea()

            VStack(spacing: 0) {
                HeaderBar(vm: vm)
                Divider().opacity(0.4)
                SearchBar(vm: vm)
                ResultsArea(vm: vm)
                StatusBar(vm: vm)
            }
        }
        .onChange(of: vm.query) { vm.onQueryChanged() }
        .onChange(of: vm.mediaFilter) {
            Task { await vm.performSearch() }
        }
    }
}
