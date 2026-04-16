class Cass < Formula
  desc "Cross-agent session search for AI coding conversations"
  homepage "https://github.com/Dicklesworthstone/coding_agent_session_search"
  version "0.2.3"
  license "MIT"

  on_macos do
    on_arm do
      url "https://github.com/Dicklesworthstone/coding_agent_session_search/releases/download/v#{version}/cass-darwin-arm64.tar.gz"
      sha256 "c06b52ad2687042480b38ce9d37b1e2637368ec201f273315f6f2c08d1e3593a"
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/Dicklesworthstone/coding_agent_session_search/releases/download/v#{version}/cass-linux-amd64.tar.gz"
      sha256 "da0941756bcb3c0eef2bb929d990a0475b4f5ecb56bd25f140690188c5e573ef"
    end
    on_arm do
      url "https://github.com/Dicklesworthstone/coding_agent_session_search/releases/download/v#{version}/cass-linux-arm64.tar.gz"
      sha256 "203af42e3604af097e1e50e31b298ac57bf7c65e7eb5c11282d05cd043470bd4"
    end
  end

  def install
    bin.install "cass"
    generate_completions_from_executable(bin/"cass", "completions")
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/cass --version")
    assert_match "health", shell_output("#{bin}/cass --help")
  end
end
