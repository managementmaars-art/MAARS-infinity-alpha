---
name: nestjs-framework
description: NestJS modules, controllers, providers, guards, interceptors, TypeORM, GraphQL, WebSockets
---

# NestJS Framework

Production-grade NestJS applications: modular architecture, controllers, services, guards, interceptors, TypeORM for database access, GraphQL API, and WebSocket support.

## Project Bootstrap

```typescript
// main.ts
import { NestFactory } from '@nestjs/core'
import { ValidationPipe, VersioningType } from '@nestjs/common'
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger'
import { AppModule } from './app.module'
import helmet from 'helmet'
import * as compression from 'compression'

async function bootstrap() {
  const app = await NestFactory.create(AppModule, {
    logger: ['error', 'warn', 'log', process.env.NODE_ENV !== 'production' ? 'debug' : 'log'],
  })

  app.use(helmet())
  app.use(compression())
  app.enableCors({ origin: process.env.CORS_ORIGINS?.split(',') ?? '*' })

  app.enableVersioning({ type: VersioningType.URI, defaultVersion: '1' })

  app.useGlobalPipes(new ValidationPipe({
    whitelist: true,            // strip unknown properties
    forbidNonWhitelisted: true, // throw on unknown properties
    transform: true,            // auto-transform to DTO types
    transformOptions: { enableImplicitConversion: true },
  }))

  const swaggerConfig = new DocumentBuilder()
    .setTitle('MyApp API')
    .setVersion('1.0')
    .addBearerAuth()
    .build()
  SwaggerModule.setup('api', app, SwaggerModule.createDocument(app, swaggerConfig))

  await app.listen(process.env.PORT ?? 3000)
  console.log(`Application running on: ${await app.getUrl()}`)
}
bootstrap()
```

## Module Structure

```typescript
// users/users.module.ts
@Module({
  imports: [
    TypeOrmModule.forFeature([UserEntity, UserProfileEntity]),
    JwtModule.registerAsync({
      imports: [ConfigModule],
      useFactory: (config: ConfigService) => ({
        secret: config.getOrThrow('JWT_SECRET'),
        signOptions: { expiresIn: '7d' },
      }),
      inject: [ConfigService],
    }),
    EventEmitterModule,
  ],
  controllers: [UsersController],
  providers: [UsersService, UsersRepository, UserMapper],
  exports: [UsersService],
})
export class UsersModule {}

// app.module.ts
@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true, validationSchema: envValidationSchema }),
    TypeOrmModule.forRootAsync({
      imports: [ConfigModule],
      useFactory: (config: ConfigService) => ({
        type: 'postgres',
        url: config.getOrThrow('DATABASE_URL'),
        entities: [__dirname + '/**/*.entity{.ts,.js}'],
        migrations: [__dirname + '/migrations/*{.ts,.js}'],
        migrationsRun: true,
        ssl: config.get('NODE_ENV') === 'production' ? { rejectUnauthorized: false } : false,
        logging: config.get('NODE_ENV') !== 'production',
      }),
      inject: [ConfigService],
    }),
    ThrottlerModule.forRoot([{ ttl: 60000, limit: 100 }]),
    UsersModule,
    AuthModule,
    EventEmitterModule.forRoot(),
  ],
})
export class AppModule {}
```

## Controllers and DTOs

```typescript
// users/dto/create-user.dto.ts
export class CreateUserDto {
  @ApiProperty({ example: 'john@example.com' })
  @IsEmail()
  @Transform(({ value }) => value.toLowerCase().trim())
  email: string

  @ApiProperty({ minLength: 2, maxLength: 100 })
  @IsString()
  @Length(2, 100)
  name: string

  @ApiProperty({ minLength: 8 })
  @IsString()
  @MinLength(8)
  @Matches(/^(?=.*[A-Z])(?=.*[0-9])/, {
    message: 'Password must contain at least one uppercase letter and one number',
  })
  password: string

  @ApiPropertyOptional({ enum: UserRole, default: UserRole.USER })
  @IsEnum(UserRole)
  @IsOptional()
  role?: UserRole = UserRole.USER
}

// users/users.controller.ts
@ApiTags('Users')
@Controller({ path: 'users', version: '1' })
@UseGuards(JwtAuthGuard, RolesGuard)
@UseInterceptors(TransformInterceptor, LoggingInterceptor)
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Get()
  @Roles(UserRole.ADMIN)
  @ApiOperation({ summary: 'List all users (admin only)' })
  @ApiOkResponse({ type: PaginatedUsersResponseDto })
  async findAll(@Query() query: PaginatedQueryDto): Promise<PaginatedUsersResponseDto> {
    return this.usersService.findAll(query)
  }

  @Get(':id')
  @ApiParam({ name: 'id', type: String, format: 'uuid' })
  async findOne(@Param('id', ParseUUIDPipe) id: string): Promise<UserResponseDto> {
    return this.usersService.findOneOrThrow(id)
  }

  @Post()
  @Public()  // custom decorator to bypass auth
  @HttpCode(HttpStatus.CREATED)
  async create(@Body() dto: CreateUserDto): Promise<UserResponseDto> {
    return this.usersService.create(dto)
  }

  @Patch(':id')
  @ApiBody({ type: UpdateUserDto })
  async update(
    @Param('id', ParseUUIDPipe) id: string,
    @Body() dto: UpdateUserDto,
    @CurrentUser() currentUser: JwtPayload,
  ): Promise<UserResponseDto> {
    if (id !== currentUser.sub && currentUser.role !== UserRole.ADMIN) {
      throw new ForbiddenException('Cannot update another user')
    }
    return this.usersService.update(id, dto)
  }

  @Delete(':id')
  @Roles(UserRole.ADMIN)
  @HttpCode(HttpStatus.NO_CONTENT)
  async remove(@Param('id', ParseUUIDPipe) id: string): Promise<void> {
    await this.usersService.remove(id)
  }
}
```

## Guards and Interceptors

```typescript
// Guards
@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {
  canActivate(context: ExecutionContext): boolean | Promise<boolean> | Observable<boolean> {
    const isPublic = this.reflector.getAllAndOverride<boolean>(IS_PUBLIC_KEY, [
      context.getHandler(),
      context.getClass(),
    ])
    if (isPublic) return true
    return super.canActivate(context)
  }
}

@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const requiredRoles = this.reflector.getAllAndMerge<UserRole[]>(ROLES_KEY, [
      context.getHandler(),
      context.getClass(),
    ])
    if (!requiredRoles?.length) return true

    const { user } = context.switchToHttp().getRequest<RequestWithUser>()
    return requiredRoles.includes(user.role)
  }
}

// Interceptors
@Injectable()
export class TransformInterceptor<T> implements NestInterceptor<T, ApiResponse<T>> {
  intercept(context: ExecutionContext, next: CallHandler<T>): Observable<ApiResponse<T>> {
    return next.handle().pipe(
      map(data => ({
        success: true,
        data,
        timestamp: new Date().toISOString(),
      }))
    )
  }
}

@Injectable()
export class LoggingInterceptor implements NestInterceptor {
  private readonly logger = new Logger(LoggingInterceptor.name)

  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const { method, url } = context.switchToHttp().getRequest()
    const now = Date.now()

    return next.handle().pipe(
      tap(() => this.logger.log(`${method} ${url} - ${Date.now() - now}ms`)),
      catchError(err => {
        this.logger.error(`${method} ${url} - ${err.message}`)
        throw err
      })
    )
  }
}
```

## TypeORM Entity and Repository

```typescript
// users/entities/user.entity.ts
@Entity('users')
@Index(['email'], { unique: true })
export class UserEntity {
  @PrimaryGeneratedColumn('uuid')
  id: string

  @Column({ length: 255 })
  email: string

  @Column({ length: 100 })
  name: string

  @Column({ select: false })  // exclude from default queries
  passwordHash: string

  @Column({ type: 'enum', enum: UserRole, default: UserRole.USER })
  role: UserRole

  @OneToMany(() => PostEntity, post => post.author, { lazy: true })
  posts: Promise<PostEntity[]>

  @CreateDateColumn()
  createdAt: Date

  @UpdateDateColumn()
  updatedAt: Date

  @DeleteDateColumn()
  deletedAt: Date  // soft delete
}

// Custom repository
@Injectable()
export class UsersRepository {
  constructor(
    @InjectRepository(UserEntity)
    private readonly repo: Repository<UserEntity>
  ) {}

  async findPaginated(
    page: number,
    limit: number,
    search?: string
  ): Promise<[UserEntity[], number]> {
    const qb = this.repo.createQueryBuilder('user')
      .where('user.deletedAt IS NULL')
    
    if (search) {
      qb.andWhere('(user.name ILIKE :search OR user.email ILIKE :search)', {
        search: `%${search}%`,
      })
    }
    
    return qb
      .orderBy('user.createdAt', 'DESC')
      .skip((page - 1) * limit)
      .take(limit)
      .getManyAndCount()
  }
}
```

## GraphQL Resolver

```typescript
// users/users.resolver.ts
@Resolver(() => User)
@UseGuards(GqlJwtAuthGuard)
export class UsersResolver {
  constructor(
    private usersService: UsersService,
    private postsService: PostsService,
  ) {}

  @Query(() => PaginatedUsers, { name: 'users' })
  @Roles(UserRole.ADMIN)
  async findAll(@Args() args: PaginatedQueryArgs): Promise<PaginatedUsers> {
    return this.usersService.findAll(args)
  }

  @Query(() => User, { name: 'user', nullable: true })
  async findOne(@Args('id', { type: () => ID }) id: string): Promise<User | null> {
    return this.usersService.findOne(id)
  }

  @Mutation(() => User)
  async createUser(@Args('input') input: CreateUserInput): Promise<User> {
    return this.usersService.create(input)
  }

  // DataLoader for N+1 prevention
  @ResolveField(() => [Post])
  async posts(
    @Parent() user: User,
    @Context() { postsLoader }: GqlContext
  ): Promise<Post[]> {
    return postsLoader.load(user.id)
  }
}
```

## WebSocket Gateway

```typescript
@WebSocketGateway({
  namespace: '/events',
  cors: { origin: process.env.CORS_ORIGINS?.split(',') },
})
@UseGuards(WsJwtGuard)
export class EventsGateway implements OnGatewayInit, OnGatewayConnection, OnGatewayDisconnect {
  @WebSocketServer() server: Server
  private readonly logger = new Logger(EventsGateway.name)

  afterInit() { this.logger.log('WebSocket gateway initialized') }
  handleConnection(client: Socket) { this.logger.log(`Client connected: ${client.id}`) }
  handleDisconnect(client: Socket) { this.logger.log(`Client disconnected: ${client.id}`) }

  @SubscribeMessage('join-room')
  handleJoinRoom(
    @MessageBody() roomId: string,
    @ConnectedSocket() client: Socket
  ): WsResponse<string> {
    client.join(roomId)
    return { event: 'joined', data: roomId }
  }

  // Emit from any service by injecting EventsGateway
  broadcastToRoom(roomId: string, event: string, data: any) {
    this.server.to(roomId).emit(event, data)
  }
}
```

## Best Practices

- Use `ConfigModule.forRoot({ isGlobal: true })` and always use `config.getOrThrow()` to fail fast on missing env vars
- Apply `ThrottlerGuard` globally for rate limiting; override per endpoint with `@SkipThrottle()` or `@Throttle()`
- Separate concerns: Controller handles HTTP → Service handles business logic → Repository handles data
- Use `@EventEmitter2` for domain events between modules (avoids circular dependencies)
- Use `ClassSerializerInterceptor` globally with `@Exclude()` / `@Expose()` on entities for safe serialization
- Use DataLoaders in GraphQL resolvers to batch N+1 queries
- Enable soft delete with `@DeleteDateColumn()` and `repo.softDelete()` for audit trails
- Write e2e tests with `@nestjs/testing` + Supertest + a test database (Testcontainers recommended)
- Use `winston` or `pino` for structured logging; integrate with `NEST_LOGGER` token
- Use migrations (not `synchronize: true`) in production — `typeorm migration:generate` and `migration:run`

## Models to Use

- **Default**: `claude-sonnet-4-5` — module design, guards, interceptors, TypeORM
- **Complex architecture**: `claude-opus-4-5` — microservices, GraphQL federation, event sourcing
- **Boilerplate**: `claude-haiku-3-5` — DTOs, entities, simple CRUD resolvers
