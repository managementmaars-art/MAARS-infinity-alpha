---
name: android-compose
cluster: mobile
description: "Jetpack Compose: @Composable, state hoisting, LazyColumn, Material 3, CompositionLocal, navigation-compose"
tags: ["compose","android","ui","material"]
dependencies: []
composes: []
similar_to: []
called_by: []
authorization_required: false
scope: general
model_hint: claude-sonnet
embedding_hint: "jetpack compose composable state material theme animation navigation"
---

# android-compose

## Purpose
This skill equips the AI to generate and manipulate Android UI code using Jetpack Compose, focusing on declarative syntax for efficient, reactive interfaces. Use it to handle UI components, state management, and navigation in Android apps.

## When to Use
Apply this skill when building or refactoring Android apps that require modern UI patterns, such as dynamic lists, theme-aware designs, or screen navigation. Use it for new projects with Material 3 or to migrate from XML layouts to Compose for better performance and code simplicity.

## Key Capabilities
- Define reusable UI elements with @Composable annotations.
- Manage state via state hoisting to avoid bugs in recomposition.
- Render efficient lists with LazyColumn for large datasets.
- Implement Material 3 components like Button and Scaffold for consistent theming.
- Access global context with CompositionLocal for sharing data across composables.
- Handle navigation using navigation-compose for multi-screen apps.

## Usage Patterns
To build a UI, start by creating a top-level @Composable function in your Activity or Fragment. Always hoist state to parent composables to enable proper recomposition. For lists, wrap items in LazyColumn to lazy-load content. Use MaterialTheme for styling and CompositionLocalProvider to inject values. When navigating, set up a NavHost with composable destinations.

## Common Commands/API
- Use @Composable annotation: Import androidx.compose.runtime.Composable; annotate functions like @Composable fun MyScreen() { Text("Hello") }
- Manage state: Use remember and mutableStateOf, e.g., val count by remember { mutableStateOf(0) }
- Lazy lists: Import androidx.compose.foundation.lazy.LazyColumn; use LazyColumn { items(list) { ItemRow(it) } }
- Material 3: Import androidx.compose.material3.MaterialTheme; wrap UI in MaterialTheme { Surface { MyContent() } }
- CompositionLocal: Define with compositionLocalOf, e.g., val LocalUser = compositionLocalOf { null }; access with LocalUser.current
- Navigation: Add dependency in build.gradle: implementation "androidx.navigation:navigation-compose:2.5.3"; set up with NavHost(navController) { composable("route") { Screen() } }

## Integration Notes
Integrate Compose into an Android project by adding the Compose BOM in build.gradle: dependencies { implementation platform('androidx.compose:compose-bom:2023.10.01') implementation 'androidx.compose.ui:ui' implementation 'androidx.compose.material3:material3' }. Enable Compose in the module's build.gradle with composeOptions { kotlinCompilerExtensionVersion '1.4.7' }. For navigation, combine with ViewModel by injecting it via hilt or manual dependency. Use $ANDROID_HOME environment for SDK paths if needed, and set $COMPOSE_VERSION for custom versions in scripts.

## Error Handling
Handle recomposition errors by ensuring state is hoisted; for example, if a composable crashes due to stale state, wrap it in a function that passes state as parameters. Common issues: Invalid changes during composition—use rememberUpdatedState for callbacks. For LazyColumn errors like IndexOutOfBounds, ensure data is loaded before rendering. Log errors with Log.e("ComposeError", "Message") and use try-catch in non-UI code. If navigation fails, check navController setup and routes; debug with Android Studio's Compose preview.

## Concrete Usage Examples
1. Simple composable with state: Create a counter UI by writing: @Composable fun Counter() { var count by remember { mutableStateOf(0) } Button(onClick = { count++ }) { Text("$count") } } Then, call it from your Activity: setContent { Counter() }
2. Navigation with LazyColumn: Set up a screen with a list: @Composable fun HomeScreen(navController: NavController) { LazyColumn { items(10) { Text("Item $it"); if (it == 5) Button(onClick = { navController.navigate("detail") }) { Text("Go") } } } } In your app: NavHost { composable("home") { HomeScreen(navController) } }

## Graph Relationships
- Related to cluster: mobile
- Connected via tags: compose (e.g., links to other UI skills), android (e.g., integrates with Android core skills), ui (e.g., shares patterns with web UI skills), material (e.g., aligns with design system skills)
- Dependencies: navigation-compose (for routing), material3 (for theming)
