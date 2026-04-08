---
name: java-spring
description: Spring Boot 3, dependency injection, JPA/Hibernate, REST controllers, Spring Security, Spring Data, testing with JUnit 5
---

# Java Spring Boot 3

Expert-level Spring Boot 3 development: building production-grade REST APIs, data persistence with JPA/Hibernate, security with Spring Security 6, and comprehensive testing.

## Project Setup

Use Spring Initializr or the Spring Boot Maven plugin. Minimum `pom.xml` dependencies:

```xml
<parent>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-parent</artifactId>
  <version>3.3.0</version>
</parent>

<dependencies>
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
  </dependency>
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
  </dependency>
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
  </dependency>
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-validation</artifactId>
  </dependency>
  <dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <scope>runtime</scope>
  </dependency>
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
  </dependency>
</dependencies>
```

## REST Controllers

Use `@RestController` with `@RequestMapping`. Prefer constructor injection. Return `ResponseEntity` for full HTTP control:

```java
@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @GetMapping
    public ResponseEntity<Page<UserDto>> listUsers(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String search) {

        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
        Page<UserDto> users = userService.findAll(search, pageable);
        return ResponseEntity.ok(users);
    }

    @GetMapping("/{id}")
    public ResponseEntity<UserDto> getUser(@PathVariable UUID id) {
        return userService.findById(id)
                .map(ResponseEntity::ok)
                .orElseThrow(() -> new ResourceNotFoundException("User not found: " + id));
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public UserDto createUser(@Valid @RequestBody CreateUserRequest request) {
        return userService.create(request);
    }

    @PutMapping("/{id}")
    public ResponseEntity<UserDto> updateUser(
            @PathVariable UUID id,
            @Valid @RequestBody UpdateUserRequest request) {
        return ResponseEntity.ok(userService.update(id, request));
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deleteUser(@PathVariable UUID id) {
        userService.delete(id);
    }
}
```

## JPA / Hibernate Entity Design

```java
@Entity
@Table(name = "users", indexes = {
    @Index(name = "idx_users_email", columnList = "email", unique = true),
    @Index(name = "idx_users_tenant", columnList = "tenant_id")
})
@EntityListeners(AuditingEntityListener.class)
@Getter
@Setter
@NoArgsConstructor
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false, unique = true, length = 255)
    private String email;

    @Column(nullable = false, length = 100)
    private String firstName;

    @Column(nullable = false, length = 100)
    private String lastName;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private UserRole role = UserRole.USER;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "tenant_id", nullable = false)
    private Tenant tenant;

    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<UserProfile> profiles = new ArrayList<>();

    @CreatedDate
    @Column(updatable = false)
    private Instant createdAt;

    @LastModifiedDate
    private Instant updatedAt;

    @Version
    private Long version; // optimistic locking
}

// Repository with custom queries
@Repository
public interface UserRepository extends JpaRepository<User, UUID>, JpaSpecificationExecutor<User> {

    Optional<User> findByEmail(String email);

    @Query("SELECT u FROM User u JOIN FETCH u.tenant WHERE u.tenant.id = :tenantId")
    List<User> findByTenantId(UUID tenantId);

    @Modifying
    @Query("UPDATE User u SET u.lastLoginAt = :now WHERE u.id = :id")
    void updateLastLogin(@Param("id") UUID id, @Param("now") Instant now);

    // Spring Data Specifications for dynamic filtering
    static Specification<User> hasEmail(String email) {
        return (root, query, cb) -> email == null ? null : cb.equal(root.get("email"), email);
    }

    static Specification<User> hasRole(UserRole role) {
        return (root, query, cb) -> role == null ? null : cb.equal(root.get("role"), role);
    }
}
```

## Spring Security 6 (JWT + Method Security)

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtFilter;
    private final UserDetailsService userDetailsService;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(AbstractHttpConfigurer::disable)
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/v1/auth/**", "/actuator/health").permitAll()
                .requestMatchers(HttpMethod.GET, "/api/v1/public/**").permitAll()
                .requestMatchers("/api/v1/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class)
            .exceptionHandling(ex -> ex
                .authenticationEntryPoint(new HttpStatusEntryPoint(HttpStatus.UNAUTHORIZED))
                .accessDeniedHandler((req, res, e) -> res.sendError(HttpStatus.FORBIDDEN.value()))
            )
            .build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(12);
    }

    @Bean
    public AuthenticationManager authManager(AuthenticationConfiguration config) throws Exception {
        return config.getAuthenticationManager();
    }
}

// JWT Filter
@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtService jwtService;
    private final UserDetailsService userDetailsService;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain) throws ServletException, IOException {
        String authHeader = request.getHeader("Authorization");
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            chain.doFilter(request, response);
            return;
        }
        String token = authHeader.substring(7);
        String username = jwtService.extractUsername(token);

        if (username != null && SecurityContextHolder.getContext().getAuthentication() == null) {
            UserDetails userDetails = userDetailsService.loadUserByUsername(username);
            if (jwtService.isValid(token, userDetails)) {
                UsernamePasswordAuthenticationToken auth = new UsernamePasswordAuthenticationToken(
                    userDetails, null, userDetails.getAuthorities());
                auth.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                SecurityContextHolder.getContext().setAuthentication(auth);
            }
        }
        chain.doFilter(request, response);
    }
}
```

## Service Layer with Transactions

```java
@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
@Slf4j
public class UserService {

    private final UserRepository userRepository;
    private final UserMapper userMapper;
    private final ApplicationEventPublisher eventPublisher;

    public Page<UserDto> findAll(String search, Pageable pageable) {
        Specification<User> spec = Specification.where(null);
        if (StringUtils.hasText(search)) {
            spec = spec.and((root, q, cb) ->
                cb.or(
                    cb.like(cb.lower(root.get("email")), "%" + search.toLowerCase() + "%"),
                    cb.like(cb.lower(root.get("firstName")), "%" + search.toLowerCase() + "%")
                )
            );
        }
        return userRepository.findAll(spec, pageable).map(userMapper::toDto);
    }

    @Transactional
    public UserDto create(CreateUserRequest request) {
        if (userRepository.findByEmail(request.email()).isPresent()) {
            throw new ConflictException("Email already registered: " + request.email());
        }
        User user = userMapper.toEntity(request);
        User saved = userRepository.save(user);
        eventPublisher.publishEvent(new UserCreatedEvent(saved.getId()));
        log.info("Created user {} with email {}", saved.getId(), saved.getEmail());
        return userMapper.toDto(saved);
    }

    @Transactional
    public UserDto update(UUID id, UpdateUserRequest request) {
        User user = userRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("User not found"));
        userMapper.updateEntity(request, user);
        return userMapper.toDto(userRepository.save(user));
    }
}
```

## Global Exception Handling

```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    public ProblemDetail handleNotFound(ResourceNotFoundException ex) {
        ProblemDetail pd = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());
        pd.setTitle("Resource Not Found");
        return pd;
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ProblemDetail handleValidation(MethodArgumentNotValidException ex) {
        Map<String, String> errors = new LinkedHashMap<>();
        ex.getBindingResult().getFieldErrors().forEach(e ->
            errors.put(e.getField(), e.getDefaultMessage()));
        ProblemDetail pd = ProblemDetail.forStatus(HttpStatus.BAD_REQUEST);
        pd.setTitle("Validation Failed");
        pd.setProperty("errors", errors);
        return pd;
    }

    @ExceptionHandler(Exception.class)
    public ProblemDetail handleUnexpected(Exception ex) {
        log.error("Unexpected error", ex);
        return ProblemDetail.forStatusAndDetail(HttpStatus.INTERNAL_SERVER_ERROR,
            "An unexpected error occurred");
    }
}
```

## Testing with JUnit 5

```java
// Unit test with Mockito
@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock UserRepository userRepository;
    @Mock UserMapper userMapper;
    @Mock ApplicationEventPublisher eventPublisher;
    @InjectMocks UserService userService;

    @Test
    void createUser_shouldPublishEvent_whenSuccessful() {
        CreateUserRequest request = new CreateUserRequest("test@example.com", "John", "Doe");
        User user = new User();
        user.setId(UUID.randomUUID());
        UserDto dto = new UserDto(user.getId(), request.email(), request.firstName(), request.lastName());

        when(userRepository.findByEmail(request.email())).thenReturn(Optional.empty());
        when(userMapper.toEntity(request)).thenReturn(user);
        when(userRepository.save(user)).thenReturn(user);
        when(userMapper.toDto(user)).thenReturn(dto);

        UserDto result = userService.create(request);

        assertThat(result.email()).isEqualTo(request.email());
        verify(eventPublisher).publishEvent(any(UserCreatedEvent.class));
    }

    @Test
    void createUser_shouldThrow_whenEmailExists() {
        CreateUserRequest request = new CreateUserRequest("dup@example.com", "Jane", "Doe");
        when(userRepository.findByEmail(request.email())).thenReturn(Optional.of(new User()));

        assertThatThrownBy(() -> userService.create(request))
            .isInstanceOf(ConflictException.class)
            .hasMessageContaining("already registered");
    }
}

// Integration test with @SpringBootTest
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureMockMvc
@Transactional
class UserControllerIntegrationTest {

    @Autowired MockMvc mockMvc;
    @Autowired ObjectMapper objectMapper;
    @Autowired UserRepository userRepository;

    @Test
    @WithMockUser(roles = "ADMIN")
    void createUser_returns201_withValidPayload() throws Exception {
        CreateUserRequest request = new CreateUserRequest("new@example.com", "Alice", "Smith");

        mockMvc.perform(post("/api/v1/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.email").value("new@example.com"))
            .andExpect(jsonPath("$.id").isNotEmpty());
    }

    @Test
    void listUsers_returns401_whenUnauthenticated() throws Exception {
        mockMvc.perform(get("/api/v1/users"))
            .andExpect(status().isUnauthorized());
    }
}
```

## Best Practices

- Use `@Transactional(readOnly = true)` at the service class level and override with `@Transactional` for write methods
- Prefer `FetchType.LAZY` on all associations; use `JOIN FETCH` in queries when you need eagerly loaded data
- Map entities to DTOs at the service layer — never expose entities directly from controllers
- Use `@Version` on entities for optimistic locking in concurrent scenarios
- Define custom exceptions (`ResourceNotFoundException`, `ConflictException`) and handle them centrally in `@RestControllerAdvice`
- Use Spring's `ProblemDetail` (RFC 9457) for structured error responses
- Enable `spring.jpa.open-in-view=false` in `application.yml` to avoid lazy loading issues
- Use `@SpringBootTest` sparingly; prefer slice tests (`@WebMvcTest`, `@DataJpaTest`) for faster feedback
- Profile with `@Profile("test")` to override beans for integration tests (e.g., use H2 or Testcontainers)
- Use `Testcontainers` for database integration tests: `@Container PostgreSQLContainer<?> postgres`

## Models to Use

- **Default**: `claude-sonnet-4-5` — handles Spring idioms, JPA nuances, security config
- **Complex architecture / large refactors**: `claude-opus-4-5` — multi-layer reasoning for system design
- **Quick snippets / boilerplate**: `claude-haiku-3-5` — fast generation of DTOs, mappers, tests
