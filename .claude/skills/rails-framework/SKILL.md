---
name: rails-framework
description: Ruby on Rails 8, ActiveRecord, controllers, Hotwire/Turbo, Action Cable, Stimulus, testing
---

# Ruby on Rails 8

Full-stack Rails 8 development: ActiveRecord with modern patterns, Hotwire (Turbo + Stimulus) for SPA-like interactivity, Action Cable for real-time features, and comprehensive testing with RSpec.

## Rails 8 Project Setup

```ruby
# Gemfile
source 'https://rubygems.org'
ruby '3.3.0'

gem 'rails', '~> 8.0.0'
gem 'pg'
gem 'puma'
gem 'solid_cache'        # DB-backed cache (Rails 8)
gem 'solid_queue'        # DB-backed queue (Rails 8)
gem 'solid_cable'        # DB-backed Action Cable (Rails 8)

# Auth
gem 'bcrypt'
gem 'jwt'

# API
gem 'jbuilder'
gem 'rack-cors'

# Assets
gem 'importmap-rails'
gem 'turbo-rails'
gem 'stimulus-rails'
gem 'tailwindcss-rails'

group :development, :test do
  gem 'rspec-rails'
  gem 'factory_bot_rails'
  gem 'faker'
  gem 'rubocop-rails-omakase', require: false
end

group :test do
  gem 'capybara'
  gem 'selenium-webdriver'
  gem 'shoulda-matchers'
  gem 'webmock'
  gem 'vcr'
end
```

## ActiveRecord Models

```ruby
# app/models/user.rb
class User < ApplicationRecord
  # Associations
  has_many :posts, dependent: :destroy
  has_many :comments, dependent: :destroy
  has_one  :profile, dependent: :destroy
  has_many :memberships, dependent: :destroy
  has_many :teams, through: :memberships

  # Auth
  has_secure_password

  # Enums (Rails 8 style)
  enum :role, { user: 0, moderator: 1, admin: 2 }, default: :user, validate: true

  # Validations
  validates :email, presence: true, uniqueness: { case_sensitive: false },
                    format: { with: URI::MailTo::EMAIL_REGEXP }
  validates :name, presence: true, length: { minimum: 2, maximum: 100 }
  validates :password, length: { minimum: 8 }, allow_nil: true

  # Callbacks
  before_validation :normalize_email
  after_create :send_welcome_email

  # Scopes
  scope :active,     -> { where(deactivated_at: nil) }
  scope :recent,     -> { order(created_at: :desc) }
  scope :search,     ->(q) { where('name ILIKE ? OR email ILIKE ?', "%#{q}%", "%#{q}%") }
  scope :with_posts, -> { joins(:posts).distinct }

  # Delegations
  delegate :bio, :avatar_url, to: :profile, allow_nil: true

  # Class methods
  def self.authenticate(email, password)
    find_by(email: email.downcase.strip)&.authenticate(password)
  end

  # Instance methods
  def display_name
    name.presence || email.split('@').first
  end

  def soft_delete!
    update!(deactivated_at: Time.current)
  end

  private

  def normalize_email
    self.email = email&.downcase&.strip
  end

  def send_welcome_email
    UserMailer.welcome(self).deliver_later
  end
end

# db/schema concern for common columns
module Auditable
  extend ActiveSupport::Concern

  included do
    before_create { self.created_by ||= Current.user&.id }
    before_update { self.updated_by = Current.user&.id }
  end
end
```

## Controllers (REST + Hotwire)

```ruby
# app/controllers/users_controller.rb
class UsersController < ApplicationController
  before_action :authenticate_user!
  before_action :set_user, only: [:show, :edit, :update, :destroy]
  before_action -> { authorize @user }, only: [:edit, :update, :destroy]

  def index
    @users = User.active
                 .search(params[:q])
                 .includes(:profile)
                 .page(params[:page]).per(20)
    
    respond_to do |format|
      format.html
      format.json { render json: @users }
      format.turbo_stream  # Hotwire partial update
    end
  end

  def create
    @user = User.new(user_params)

    respond_to do |format|
      if @user.save
        format.html { redirect_to @user, notice: 'User created successfully.' }
        format.json { render json: @user, status: :created }
        format.turbo_stream
      else
        format.html { render :new, status: :unprocessable_entity }
        format.json { render json: { errors: @user.errors }, status: :unprocessable_entity }
        format.turbo_stream { render turbo_stream: turbo_stream.replace('user-form', partial: 'form', locals: { user: @user }) }
      end
    end
  end

  def destroy
    @user.soft_delete!
    respond_to do |format|
      format.html { redirect_to users_url, notice: 'User deactivated.' }
      format.turbo_stream { render turbo_stream: turbo_stream.remove("user_#{@user.id}") }
    end
  end

  private

  def set_user
    @user = User.find(params[:id])
  end

  def user_params
    params.require(:user).permit(:name, :email, :password, :password_confirmation, :role)
  end
end
```

## Hotwire Turbo Streams

```erb
<%# app/views/users/create.turbo_stream.erb %>
<%= turbo_stream.prepend 'users-list', partial: 'users/user', locals: { user: @user } %>
<%= turbo_stream.replace 'user-form', partial: 'users/form', locals: { user: User.new } %>
<%= turbo_stream.update 'flash', partial: 'shared/flash', locals: { notice: 'User created!' } %>

<%# app/views/users/index.html.erb %>
<div id="users-list">
  <%= render @users %>
</div>

<%= turbo_frame_tag 'user-pagination' do %>
  <%= paginate @users %>
<% end %>

<%# Infinite scroll with Turbo Frames %>
<%= turbo_frame_tag "users_page_#{@users.next_page}", loading: :lazy,
    src: users_path(page: @users.next_page) do %>
  <div class="loading-spinner">Loading...</div>
<% end %>
```

## Stimulus Controllers

```javascript
// app/javascript/controllers/search_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["input", "results", "loading"]
  static values = { url: String, delay: { type: Number, default: 300 } }

  connect() {
    this.timeout = null
  }

  search() {
    clearTimeout(this.timeout)
    this.timeout = setTimeout(() => this.#performSearch(), this.delayValue)
  }

  async #performSearch() {
    const query = this.inputTarget.value.trim()
    if (query.length < 2) return

    this.loadingTarget.classList.remove("hidden")

    const url = new URL(this.urlValue, window.location.origin)
    url.searchParams.set("q", query)
    url.searchParams.set("format", "turbo_stream")

    const response = await fetch(url, {
      headers: { Accept: "text/vnd.turbo-stream.html" }
    })

    if (response.ok) {
      const html = await response.text()
      Turbo.renderStreamMessage(html)
    }

    this.loadingTarget.classList.add("hidden")
  }
}
```

## Action Cable (Real-time)

```ruby
# app/channels/room_channel.rb
class RoomChannel < ApplicationCable::Channel
  def subscribed
    room = Room.find(params[:room_id])
    reject unless current_user.member_of?(room)
    stream_for room
  end

  def receive(data)
    message = Message.create!(
      content: data['content'],
      room_id: params[:room_id],
      user: current_user
    )
    RoomChannel.broadcast_to(message.room, {
      event: 'new_message',
      html: ApplicationController.render(
        partial: 'messages/message',
        locals: { message: }
      )
    })
  end
end

# app/models/message.rb — broadcast after create
class Message < ApplicationRecord
  belongs_to :room
  belongs_to :user
  after_create_commit -> { broadcast_message }

  private

  def broadcast_message
    RoomChannel.broadcast_to(room, event: 'new_message',
      html: ApplicationController.render(partial: 'messages/message', locals: { message: self }))
  end
end
```

## RSpec Testing

```ruby
# spec/models/user_spec.rb
RSpec.describe User, type: :model do
  subject(:user) { build(:user) }

  it { is_expected.to be_valid }
  it { is_expected.to have_secure_password }
  it { is_expected.to validate_presence_of(:email) }
  it { is_expected.to validate_uniqueness_of(:email).case_insensitive }
  it { is_expected.to have_many(:posts).dependent(:destroy) }

  describe '.authenticate' do
    let!(:user) { create(:user, password: 'Password1') }

    it 'returns user with correct credentials' do
      expect(User.authenticate(user.email, 'Password1')).to eq(user)
    end

    it 'returns false with wrong password' do
      expect(User.authenticate(user.email, 'wrong')).to be_falsy
    end
  end
end

# spec/requests/users_spec.rb
RSpec.describe 'Users API', type: :request do
  let(:admin) { create(:user, :admin) }
  let(:headers) { { 'Authorization' => "Bearer #{generate_token(admin)}" } }

  describe 'GET /users' do
    let!(:users) { create_list(:user, 3) }

    it 'returns paginated users' do
      get '/users', headers: headers
      expect(response).to have_http_status(:ok)
      expect(json['data'].length).to eq(3)
    end
  end

  describe 'POST /users' do
    let(:params) { { user: attributes_for(:user) } }

    it 'creates a user and returns 201' do
      expect {
        post '/users', params:, headers:, as: :json
      }.to change(User, :count).by(1)
      expect(response).to have_http_status(:created)
    end

    it 'returns validation errors on invalid input' do
      post '/users', params: { user: { email: 'bad' } }, headers:, as: :json
      expect(response).to have_http_status(:unprocessable_entity)
      expect(json['errors']['email']).to be_present
    end
  end
end

# spec/system/user_search_spec.rb
RSpec.describe 'User Search', type: :system do
  let(:admin) { create(:user, :admin) }
  before { sign_in admin }

  it 'filters users by name in real time', js: true do
    create(:user, name: 'Alice Johnson')
    create(:user, name: 'Bob Smith')

    visit users_path
    fill_in 'Search', with: 'Alice'

    expect(page).to have_content('Alice Johnson')
    expect(page).not_to have_content('Bob Smith')
  end
end
```

## Best Practices

- Use `solid_queue` for background jobs and `solid_cache` for caching — they work without Redis in Rails 8
- Prefer `turbo_stream` responses over JavaScript for server-driven UI updates
- Use `Current` attributes for request context (e.g., `Current.user`) instead of thread-local variables
- Scope all database queries — never use raw `User.all` in controllers; always scope or paginate
- Use `includes` / `preload` / `eager_load` to prevent N+1 queries; detect them with `bullet` gem
- Use `strong_parameters` in `permit` — never `permit!` in production
- Run `rubocop --autocorrect` and `brakeman` in CI for style and security
- Use `FactoryBot` traits for flexible test fixtures: `create(:user, :admin, :with_posts)`
- Use `VCR` to record/replay external HTTP requests in tests for speed and reliability
- Use `propshaft` (Rails 8 default) over Sprockets for asset management

## Models to Use

- **Default**: `claude-sonnet-4-5` — ActiveRecord, controllers, Hotwire, RSpec
- **Architecture**: `claude-opus-4-5` — complex domain models, Service Objects, Event Sourcing
- **Boilerplate**: `claude-haiku-3-5` — migrations, factories, simple CRUD, scopes
