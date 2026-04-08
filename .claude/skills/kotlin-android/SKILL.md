---
name: kotlin-android
description: Kotlin, Jetpack Compose, Coroutines, Flow, Room, Retrofit, Hilt DI, Material 3
---

# Kotlin Android Development

Production-quality Android development using Kotlin, Jetpack Compose for UI, Coroutines and Flow for async/reactive programming, Room for local persistence, Retrofit for networking, Hilt for dependency injection, and Material 3 design.

## Project Structure (Multi-Module MVVM)

```
app/
  src/main/
    feature/home/          # Feature module
      HomeScreen.kt
      HomeViewModel.kt
    feature/profile/
    core/
      data/                # Repository implementations
      domain/              # Use cases + models
      network/             # Retrofit setup
      database/            # Room setup
      di/                  # Hilt modules
      ui/theme/            # Material 3 theme
```

## Hilt Dependency Injection

```kotlin
// Application class
@HiltAndroidApp
class MyApplication : Application()

// Hilt module for network
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(authInterceptor: AuthInterceptor): OkHttpClient =
        OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BODY
                        else HttpLoggingInterceptor.Level.NONE
            })
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit =
        Retrofit.Builder()
            .baseUrl(BuildConfig.BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(MoshiConverterFactory.create(
                Moshi.Builder().addLast(KotlinJsonAdapterFactory()).build()
            ))
            .build()

    @Provides
    @Singleton
    fun provideUserApi(retrofit: Retrofit): UserApi = retrofit.create(UserApi::class.java)
}

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase =
        Room.databaseBuilder(context, AppDatabase::class.java, "app_database")
            .fallbackToDestructiveMigrationOnDowngrade()
            .build()

    @Provides fun provideUserDao(db: AppDatabase): UserDao = db.userDao()
}
```

## Jetpack Compose UI with Material 3

```kotlin
@HiltViewModel
class HomeViewModel @Inject constructor(
    private val getUsersUseCase: GetUsersUseCase,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    val searchQuery = savedStateHandle.getStateFlow("search", "")

    val users: StateFlow<PagingData<User>> = searchQuery
        .debounce(300)
        .flatMapLatest { query -> getUsersUseCase(query) }
        .cachedIn(viewModelScope)
        .stateIn(viewModelScope, SharingStarted.Lazily, PagingData.empty())

    fun onSearchChange(query: String) {
        savedStateHandle["search"] = query
    }

    fun retry() = viewModelScope.launch {
        _uiState.update { it.copy(error = null) }
        // trigger reload
    }
}

data class HomeUiState(
    val isLoading: Boolean = false,
    val error: String? = null
)

// Composable screen
@Composable
fun HomeScreen(
    viewModel: HomeViewModel = hiltViewModel(),
    onUserClick: (String) -> Unit
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val users = viewModel.users.collectAsLazyPagingItems()
    val searchQuery by viewModel.searchQuery.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Users") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            )
        }
    ) { paddingValues ->
        Column(modifier = Modifier
            .fillMaxSize()
            .padding(paddingValues)) {

            SearchBar(
                query = searchQuery,
                onQueryChange = viewModel::onSearchChange,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp)
            )

            when {
                users.loadState.refresh is LoadState.Loading -> {
                    LoadingIndicator(modifier = Modifier.fillMaxSize())
                }
                users.loadState.refresh is LoadState.Error -> {
                    ErrorState(
                        message = (users.loadState.refresh as LoadState.Error).error.message ?: "Error",
                        onRetry = users::retry
                    )
                }
                else -> {
                    LazyColumn(
                        contentPadding = PaddingValues(16.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        items(users.itemCount, key = { users.peek(it)?.id ?: it }) { index ->
                            users[index]?.let { user ->
                                UserCard(user = user, onClick = { onUserClick(user.id) })
                            }
                        }
                        item {
                            if (users.loadState.append is LoadState.Loading) {
                                CircularProgressIndicator(modifier = Modifier.fillMaxWidth().wrapContentWidth())
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun UserCard(user: User, onClick: () -> Unit) {
    Card(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth(),
        shape = MaterialTheme.shapes.medium,
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(modifier = Modifier.padding(16.dp), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            AsyncImage(
                model = user.avatarUrl,
                contentDescription = "Avatar for ${user.name}",
                modifier = Modifier.size(48.dp).clip(CircleShape),
                contentScale = ContentScale.Crop
            )
            Column {
                Text(user.name, style = MaterialTheme.typography.titleMedium)
                Text(user.email, style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }
    }
}
```

## Room Database

```kotlin
// Entity
@Entity(
    tableName = "users",
    indices = [Index("email", unique = true), Index("tenant_id")]
)
data class UserEntity(
    @PrimaryKey val id: String,
    val email: String,
    val name: String,
    @ColumnInfo(name = "avatar_url") val avatarUrl: String?,
    @ColumnInfo(name = "tenant_id") val tenantId: String,
    @ColumnInfo(name = "created_at") val createdAt: Long = System.currentTimeMillis()
)

// DAO
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE tenant_id = :tenantId ORDER BY name ASC")
    fun observeByTenant(tenantId: String): Flow<List<UserEntity>>

    @Query("SELECT * FROM users WHERE name LIKE '%' || :query || '%' OR email LIKE '%' || :query || '%'")
    fun search(query: String): PagingSource<Int, UserEntity>

    @Upsert
    suspend fun upsertAll(users: List<UserEntity>)

    @Delete
    suspend fun delete(user: UserEntity)

    @Query("DELETE FROM users WHERE tenant_id = :tenantId")
    suspend fun deleteByTenant(tenantId: String)

    @Transaction
    suspend fun replaceAll(tenantId: String, users: List<UserEntity>) {
        deleteByTenant(tenantId)
        upsertAll(users)
    }
}

// Database
@Database(entities = [UserEntity::class, TaskEntity::class], version = 2, exportSchema = true)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun taskDao(): TaskDao
}
```

## Retrofit API Service

```kotlin
interface UserApi {

    @GET("users")
    suspend fun getUsers(
        @Query("page") page: Int,
        @Query("per_page") perPage: Int,
        @Query("q") query: String? = null
    ): ApiResponse<List<UserDto>>

    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: String): UserDto

    @POST("users")
    suspend fun createUser(@Body request: CreateUserRequest): UserDto

    @PUT("users/{id}")
    suspend fun updateUser(@Path("id") id: String, @Body request: UpdateUserRequest): UserDto

    @DELETE("users/{id}")
    suspend fun deleteUser(@Path("id") id: String): Response<Unit>
}

// Repository with offline-first pattern
class UserRepositoryImpl @Inject constructor(
    private val api: UserApi,
    private val dao: UserDao,
    private val mapper: UserMapper,
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher
) : UserRepository {

    override fun getUsersStream(tenantId: String): Flow<Result<List<User>>> = flow {
        // Emit cached data first
        dao.observeByTenant(tenantId)
            .map { entities -> Result.success(entities.map(mapper::toDomain)) }
            .collect { emit(it) }
    }.flowOn(ioDispatcher)

    override suspend fun syncUsers(tenantId: String): Result<Unit> = withContext(ioDispatcher) {
        runCatching {
            val response = api.getUsers(page = 1, perPage = 100)
            val entities = response.data.map(mapper::toEntity)
            dao.replaceAll(tenantId, entities)
        }
    }
}
```

## Coroutines and Flow Patterns

```kotlin
// Combining multiple flows
class DashboardViewModel @Inject constructor(
    getUsersUseCase: GetUsersUseCase,
    getTasksUseCase: GetTasksUseCase,
    getStatsUseCase: GetStatsUseCase
) : ViewModel() {

    val dashboardState: StateFlow<DashboardState> = combine(
        getUsersUseCase(),
        getTasksUseCase(),
        getStatsUseCase()
    ) { users, tasks, stats ->
        DashboardState(users = users, tasks = tasks, stats = stats)
    }
    .catch { error -> emit(DashboardState(error = error.message)) }
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = DashboardState(isLoading = true)
    )
}

// Channel for one-shot events
class LoginViewModel @Inject constructor(private val loginUseCase: LoginUseCase) : ViewModel() {
    private val _events = Channel<LoginEvent>(Channel.BUFFERED)
    val events = _events.receiveAsFlow()

    fun login(email: String, password: String) = viewModelScope.launch {
        val result = loginUseCase(email, password)
        result.fold(
            onSuccess = { _events.send(LoginEvent.NavigateToHome) },
            onFailure = { _events.send(LoginEvent.ShowError(it.message ?: "Login failed")) }
        )
    }
}

sealed class LoginEvent {
    data object NavigateToHome : LoginEvent()
    data class ShowError(val message: String) : LoginEvent()
}
```

## Material 3 Theme

```kotlin
private val LightColorScheme = lightColorScheme(
    primary = Color(0xFF1B6EF3),
    onPrimary = Color.White,
    primaryContainer = Color(0xFFD8E4FF),
    secondary = Color(0xFF5E6478),
    surface = Color(0xFFF8F9FF),
    background = Color(0xFFF8F9FF),
)

private val DarkColorScheme = darkColorScheme(
    primary = Color(0xFFAEC6FF),
    onPrimary = Color(0xFF002D6E),
    primaryContainer = Color(0xFF0045A2),
    secondary = Color(0xFFC0C5DC),
    surface = Color(0xFF111318),
    background = Color(0xFF111318),
)

@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            if (darkTheme) dynamicDarkColorScheme(LocalContext.current)
            else dynamicLightColorScheme(LocalContext.current)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = AppTypography,
        shapes = AppShapes,
        content = content
    )
}
```

## Best Practices

- Use `StateFlow` with `SharingStarted.WhileSubscribed(5_000)` to automatically cancel upstream collection when UI is gone
- Prefer `Channel` for one-shot events (navigation, toasts) — never use `SharedFlow` for events
- Always use `collectAsStateWithLifecycle()` (not `collectAsState()`) to respect lifecycle in Compose
- Use `@Stable` and `@Immutable` annotations on Compose state classes for recomposition optimization
- Define custom `CoroutineDispatcher` qualifiers (`@IoDispatcher`, `@MainDispatcher`) for testability
- Use `SavedStateHandle` in ViewModels to survive process death
- Prefer `Upsert` over Insert+Update in Room for cleaner conflict resolution
- Use `Pager` + `RemoteMediator` for network+database paging
- Enable `Room.enableMultiInstanceInvalidation()` for multi-process apps
- Run lint, detekt, and KSP (for Hilt/Room) in CI before merge

## Models to Use

- **Default**: `claude-sonnet-4-5` — Compose UI, Coroutines, Room, Hilt wiring
- **Architecture / complex flows**: `claude-opus-4-5` — multi-module design, complex state management
- **Boilerplate**: `claude-haiku-3-5` — entity classes, DAO methods, mapper functions
