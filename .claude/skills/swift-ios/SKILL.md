---
name: swift-ios
description: Swift 6, SwiftUI, Combine, async/await, Core Data, URLSession, App Store submission
---

# Swift iOS Development

Production-quality iOS app development using Swift 6, SwiftUI declarative UI, Combine reactive patterns, async/await concurrency, Core Data persistence, and App Store deployment.

## Project Architecture (MVVM + Clean)

Organize code in layers: `Presentation` (Views + ViewModels), `Domain` (UseCases + Entities), `Data` (Repositories + Services).

```swift
// Domain Entity
struct User: Identifiable, Codable, Sendable {
    let id: UUID
    var email: String
    var displayName: String
    var avatarURL: URL?
    var createdAt: Date
}

// Repository Protocol (Domain layer)
protocol UserRepository: Sendable {
    func fetchUser(id: UUID) async throws -> User
    func updateUser(_ user: User) async throws -> User
    func deleteUser(id: UUID) async throws
}

// Use Case
struct FetchUserUseCase: Sendable {
    private let repository: any UserRepository

    init(repository: any UserRepository) {
        self.repository = repository
    }

    func execute(id: UUID) async throws -> User {
        try await repository.fetchUser(id: id)
    }
}
```

## SwiftUI Views with @Observable

Swift 6 uses `@Observable` macro (Observation framework) instead of `ObservableObject`:

```swift
import SwiftUI
import Observation

@Observable
final class UserListViewModel {
    var users: [User] = []
    var isLoading = false
    var errorMessage: String?
    var searchText = ""

    private let fetchUsersUseCase: FetchUsersUseCase

    init(fetchUsersUseCase: FetchUsersUseCase) {
        self.fetchUsersUseCase = fetchUsersUseCase
    }

    var filteredUsers: [User] {
        guard !searchText.isEmpty else { return users }
        return users.filter { $0.displayName.localizedCaseInsensitiveContains(searchText) }
    }

    @MainActor
    func loadUsers() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        do {
            users = try await fetchUsersUseCase.execute()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

struct UserListView: View {
    @State private var viewModel: UserListViewModel
    @State private var selectedUser: User?

    init(viewModel: UserListViewModel) {
        self._viewModel = State(initialValue: viewModel)
    }

    var body: some View {
        NavigationSplitView {
            Group {
                if viewModel.isLoading {
                    ProgressView("Loading...")
                } else if let error = viewModel.errorMessage {
                    ContentUnavailableView(
                        "Failed to Load",
                        systemImage: "exclamationmark.triangle",
                        description: Text(error)
                    )
                } else {
                    List(viewModel.filteredUsers, selection: $selectedUser) { user in
                        UserRowView(user: user)
                            .tag(user)
                    }
                    .searchable(text: $viewModel.searchText)
                    .refreshable {
                        await viewModel.loadUsers()
                    }
                }
            }
            .navigationTitle("Users")
        } detail: {
            if let user = selectedUser {
                UserDetailView(user: user)
            } else {
                ContentUnavailableView("Select a User", systemImage: "person.circle")
            }
        }
        .task {
            await viewModel.loadUsers()
        }
    }
}

struct UserRowView: View {
    let user: User

    var body: some View {
        HStack(spacing: 12) {
            AsyncImage(url: user.avatarURL) { image in
                image.resizable().scaledToFill()
            } placeholder: {
                Image(systemName: "person.circle.fill")
                    .foregroundStyle(.secondary)
            }
            .frame(width: 44, height: 44)
            .clipShape(.circle)

            VStack(alignment: .leading, spacing: 2) {
                Text(user.displayName)
                    .font(.headline)
                Text(user.email)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
        .padding(.vertical, 4)
    }
}
```

## async/await Networking with URLSession

```swift
// API Client using structured concurrency
actor APIClient {
    private let session: URLSession
    private let baseURL: URL
    private let decoder: JSONDecoder

    init(baseURL: URL, session: URLSession = .shared) {
        self.baseURL = baseURL
        self.session = session
        self.decoder = JSONDecoder()
        self.decoder.keyDecodingStrategy = .convertFromSnakeCase
        self.decoder.dateDecodingStrategy = .iso8601
    }

    func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T {
        let urlRequest = try endpoint.urlRequest(baseURL: baseURL)
        let (data, response) = try await session.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        switch httpResponse.statusCode {
        case 200...299:
            return try decoder.decode(T.self, from: data)
        case 401:
            throw APIError.unauthorized
        case 404:
            throw APIError.notFound
        case 422:
            let error = try decoder.decode(ValidationError.self, from: data)
            throw APIError.validationFailed(error)
        default:
            throw APIError.serverError(httpResponse.statusCode)
        }
    }
}

// Endpoint definition
struct Endpoint {
    let path: String
    let method: HTTPMethod
    let queryItems: [URLQueryItem]?
    let body: (any Encodable)?
    let headers: [String: String]

    func urlRequest(baseURL: URL) throws -> URLRequest {
        var components = URLComponents(url: baseURL.appendingPathComponent(path), resolvingAgainstBaseURL: true)!
        components.queryItems = queryItems

        var request = URLRequest(url: components.url!)
        request.httpMethod = method.rawValue
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        headers.forEach { request.setValue($1, forHTTPHeaderField: $0) }

        if let body {
            let encoder = JSONEncoder()
            encoder.keyEncodingStrategy = .convertToSnakeCase
            request.httpBody = try encoder.encode(body)
        }
        return request
    }
}

enum HTTPMethod: String { case get = "GET", post = "POST", put = "PUT", delete = "DELETE" }
```

## Core Data with Swift Concurrency

```swift
// Core Data Stack
@MainActor
final class PersistenceController {
    static let shared = PersistenceController()

    let container: NSPersistentCloudKitContainer

    init(inMemory: Bool = false) {
        container = NSPersistentCloudKitContainer(name: "AppModel")
        if inMemory {
            container.persistentStoreDescriptions.first?.url = URL(fileURLWithPath: "/dev/null")
        }
        container.loadPersistentStores { _, error in
            if let error { fatalError("Core Data failed: \(error)") }
        }
        container.viewContext.automaticallyMergesChangesFromParent = true
        container.viewContext.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy
    }

    // Background save
    func save(context: NSManagedObjectContext) {
        guard context.hasChanges else { return }
        do {
            try context.save()
        } catch {
            print("Core Data save error: \(error)")
        }
    }

    func newBackgroundContext() -> NSManagedObjectContext {
        let ctx = container.newBackgroundContext()
        ctx.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy
        return ctx
    }
}

// SwiftUI usage with @FetchRequest
struct TaskListView: View {
    @Environment(\.managedObjectContext) private var viewContext

    @FetchRequest(
        sortDescriptors: [SortDescriptor(\.createdAt, order: .reverse)],
        predicate: NSPredicate(format: "isCompleted == NO"),
        animation: .default
    )
    private var tasks: FetchedResults<TaskEntity>

    var body: some View {
        List {
            ForEach(tasks) { task in
                TaskRowView(task: task)
            }
            .onDelete(perform: deleteTasks)
        }
    }

    private func deleteTasks(at offsets: IndexSet) {
        offsets.map { tasks[$0] }.forEach(viewContext.delete)
        PersistenceController.shared.save(context: viewContext)
    }
}
```

## Combine for Reactive Patterns

```swift
import Combine

final class SearchViewModel: ObservableObject {
    @Published var query = ""
    @Published private(set) var results: [SearchResult] = []
    @Published private(set) var isSearching = false

    private var cancellables = Set<AnyCancellable>()
    private let searchService: SearchService

    init(searchService: SearchService) {
        self.searchService = searchService
        setupSearch()
    }

    private func setupSearch() {
        $query
            .debounce(for: .milliseconds(300), scheduler: RunLoop.main)
            .removeDuplicates()
            .filter { $0.count >= 2 }
            .handleEvents(receiveOutput: { [weak self] _ in self?.isSearching = true })
            .flatMap { [weak self] query -> AnyPublisher<[SearchResult], Never> in
                guard let self else { return Just([]).eraseToAnyPublisher() }
                return self.searchService.search(query: query)
                    .catch { _ in Just([]) }
                    .eraseToAnyPublisher()
            }
            .receive(on: DispatchQueue.main)
            .sink { [weak self] results in
                self?.results = results
                self?.isSearching = false
            }
            .store(in: &cancellables)
    }
}
```

## App Store Submission Checklist

```swift
// Privacy manifest (PrivacyInfo.xcprivacy) — required since iOS 17.4
// Declare all NSPrivacyAccessedAPITypes usage

// App Store Connect requirements:
// 1. Bundle ID matches provisioning profile
// 2. App icons: 1024x1024 (App Store) — use AppIcon asset catalog
// 3. Launch Screen Storyboard or LaunchScreen.storyboard
// 4. Capabilities match entitlements in provisioning profile
// 5. Export Compliance — set ITSAppUsesNonExemptEncryption in Info.plist

// Info.plist privacy strings (required for App Review):
// NSCameraUsageDescription, NSPhotoLibraryUsageDescription, etc.

// Automated archive + upload with Fastlane:
// fastlane pilot upload --ipa MyApp.ipa --skip_submission

// Xcode Cloud workflow or GitHub Actions:
// xcodebuild archive -scheme MyApp -archivePath build/MyApp.xcarchive
// xcodebuild -exportArchive -archivePath build/MyApp.xcarchive \
//            -exportOptionsPlist ExportOptions.plist \
//            -exportPath build/

// ExportOptions.plist
let exportOptions = """
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0"><dict>
  <key>method</key><string>app-store</string>
  <key>teamID</key><string>YOUR_TEAM_ID</string>
  <key>uploadSymbols</key><true/>
  <key>compileBitcode</key><false/>
</dict></plist>
"""
```

## Best Practices

- Use Swift 6 strict concurrency: mark types as `Sendable`, use `@MainActor` for UI updates, use `actor` for shared mutable state
- Prefer `@Observable` over `ObservableObject` — it's more granular and efficient
- Use `task(id:)` modifier to automatically cancel and restart async tasks when dependencies change
- Avoid `DispatchQueue` in Swift 6 — use structured concurrency (`async let`, `TaskGroup`, `actor`)
- Use `@Environment` for dependency injection in SwiftUI; inject ViewModels via initializers
- Enable `SWIFT_STRICT_CONCURRENCY = complete` in build settings to catch data races at compile time
- Use Testcontainers or in-memory Core Data stacks for unit tests
- Always declare `NSPrivacyAccessedAPITypes` in `PrivacyInfo.xcprivacy` to avoid App Store rejection
- Use `withAnimation` judiciously — prefer implicit animations via `.animation(.default, value:)`
- Set `minimumDeploymentTarget` to iOS 17+ to use all `@Observable` and SwiftData features

## Models to Use

- **Default**: `claude-sonnet-4-5` — SwiftUI layouts, async patterns, Core Data
- **Architecture decisions**: `claude-opus-4-5` — Clean Architecture, complex concurrency design
- **Quick fixes / snippets**: `claude-haiku-3-5` — boilerplate, simple view components
