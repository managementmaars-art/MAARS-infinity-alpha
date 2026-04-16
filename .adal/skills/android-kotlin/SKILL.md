---
name: android-kotlin
cluster: mobile
description: "Kotlin for Android: ViewModel, LiveData/StateFlow, coroutines viewModelScope, Gradle KTS, KTX"
tags: ["kotlin","android","viewmodel","coroutines"]
dependencies: []
composes: []
similar_to: []
called_by: []
authorization_required: false
scope: general
model_hint: claude-sonnet
embedding_hint: "android kotlin viewmodel coroutines stateflow activity fragment ktx"
---

# android-kotlin

## Purpose
This skill provides guidance on using Kotlin for Android development, focusing on key components like ViewModel for state management, LiveData or StateFlow for reactive data, coroutines with viewModelScope for asynchronous operations, Gradle KTS for build configuration, and KTX for Android extensions. It helps in building robust, maintainable Android apps.

## When to Use
Use this skill when developing Android apps in Kotlin that require: managing UI state with ViewModel; handling asynchronous tasks like network calls using coroutines; observing data changes with LiveData or StateFlow; configuring projects via Gradle KTS; or simplifying code with KTX extensions. Apply it in scenarios involving activities, fragments, or services where lifecycle-aware components are needed.

## Key Capabilities
- ViewModel: Persists UI-related data across configuration changes; use `androidx.lifecycle.ViewModel` class.
- LiveData/StateFlow: Observes data changes; LiveData integrates with lifecycle, StateFlow uses Kotlin flows for reactive programming.
- Coroutines: Manage asynchronous code with `viewModelScope.launch {}` for scoped coroutines that cancel on ViewModel destruction.
- Gradle KTS: Write build scripts in Kotlin script format for better type safety, e.g., `build.gradle.kts`.
- KTX: Provides extension functions for Android APIs, like `ContextCompat` from `androidx.core`.

## Usage Patterns
To implement MVVM architecture, create a ViewModel to hold data and business logic, then observe it in activities or fragments. For asynchronous operations, always launch coroutines within viewModelScope to avoid leaks. Use LiveData for simple observations or StateFlow for more advanced flows. When configuring Gradle, switch to KTS by renaming `build.gradle` to `build.gradle.kts` and updating syntax. Integrate KTX by adding dependencies in build.gradle.kts, e.g., `implementation "androidx.core:core-ktx:1.7.0"`.

## Common Commands/API
- Gradle commands: Run builds with `./gradlew build --stacktrace` for debugging; use `./gradlew assembleDebug` to build debug APK.
- ViewModel API: Extend `ViewModel` class; example: `class MyViewModel : ViewModel() { val data = MutableLiveData<String>() }`.
- Coroutines API: Import `kotlinx.coroutines`; use `viewModelScope.launch { delay(1000); data.value = "Updated" }` for delayed updates.
- LiveData/StateFlow: Create with `val liveData = MutableLiveData<String>()`; or `val stateFlow = MutableStateFlow("")`.
- KTX extensions: Use `requireContext().toast("Message")` from `androidx.fragment.app.Fragment` KTX for showing toasts.
- Config formats: In build.gradle.kts, define dependencies as `dependencies { implementation("com.android.tools.build:gradle:7.0.0") }`; set API keys via environment variables like `buildConfigField "String", "API_KEY", "\"$SYSTEM_ENV_API_KEY\""`.

## Integration Notes
To integrate ViewModel, add `androidx.lifecycle:lifecycle-viewmodel-ktx:2.4.0` to build.gradle.kts, then inject it using `ViewModelProvider(this).get(MyViewModel::class.java)`. For coroutines, include `org.jetbrains.kotlinx:kotlinx-coroutines-android:1.6.0` and ensure `viewModelScope` is used in ViewModel subclasses. When using StateFlow, combine with `lifecycleScope.launchWhenStarted { viewModel.stateFlow.collect { updateUI(it) } }` in fragments. For auth, handle API keys by setting them as environment variables (e.g., `$ANDROID_API_KEY`) and accessing via `BuildConfig.API_KEY`. Ensure AndroidX compatibility by migrating from support libraries.

## Error Handling
Handle exceptions in coroutines with try-catch blocks: `viewModelScope.launch { try { val result = apiCall() } catch (e: Exception) { data.value = "Error: ${e.message}" } }`. For LiveData, use `observe` with lifecycle owner and handle null values: `viewModel.data.observe(this) { if (it != null) updateUI(it) else showError() }`. In Gradle, debug builds with `--stacktrace` or `--debug` flags, e.g., `./gradlew build --stacktrace`. Monitor StateFlow errors by wrapping emissions in try-catch during collection. Always check for null in KTX extensions, like `if (context != null) context.startActivity(intent)`.

## Concrete Usage Examples
1. **ViewModel with LiveData**: Create a ViewModel for user data: `class UserViewModel : ViewModel() { val userData = MutableLiveData<String>() fun loadData() { userData.value = "Loaded" } }`. In an activity: `val viewModel: UserViewModel by viewModels(); viewModel.userData.observe(this) { textView.text = it }`. Call `viewModel.loadData()` on button click.
2. **Coroutines in ViewModel**: Fetch data asynchronously: `class DataViewModel : ViewModel() { fun fetchData() = viewModelScope.launch { val result = withContext(Dispatchers.IO) { apiService.getData() } data.value = result } }`. Observe in fragment: `viewModel.data.observe(viewLifecycleOwner) { if (it.isSuccess) showData(it) else handleError() }`.

## Graph Relationships
- Related to: mobile cluster (as a sub-skill), kotlin-core skill (shares language base), android-core skill (overlaps on platform), viewmodel skill (direct dependency), coroutines skill (for async handling).
- Connections: Integrates with mobile ecosystem; depends on kotlin for syntax; links to android for platform specifics; collaborates with viewmodel and coroutines tags for advanced features.
