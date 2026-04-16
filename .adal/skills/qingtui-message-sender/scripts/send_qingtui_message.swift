#!/usr/bin/env swift

import AppKit
import ApplicationServices
import Foundation
import Vision

typealias UIElement = AXUIElement

private let qingtuiBundleID = "com.google.Chrome.app.edakdhkhbiofkngnnigocdhlhiielmad"
private let qingtuiAppName = "轻推"

struct Options {
    let contact: String
    let message: String
    let dryRun: Bool
    let timeout: TimeInterval
}

struct OCRText {
    let text: String
    let box: CGRect

    var midX: CGFloat { box.midX }
    var midY: CGFloat { box.midY }
}

enum ScriptError: LocalizedError {
    case usage(String)
    case missingAccessibilityPermission
    case qingtuiNotInstalled
    case qingtuiLaunchFailed
    case chatWindowNotFound
    case screenCaptureFailed
    case contactNotFound(String)
    case openedWrongChat(expected: String, actual: String)
    case messageDraftFailed(String)
    case messageNotSent(String)

    var errorDescription: String? {
        switch self {
        case .usage(let detail):
            return detail
        case .missingAccessibilityPermission:
            return "缺少辅助功能权限，请在“系统设置 -> 隐私与安全性 -> 辅助功能”里放行当前终端或 Codex。"
        case .qingtuiNotInstalled:
            return "未找到轻推桌面版。"
        case .qingtuiLaunchFailed:
            return "轻推启动失败。"
        case .chatWindowNotFound:
            return "未找到轻推主窗口。"
        case .screenCaptureFailed:
            return "轻推窗口截图失败。请确认当前终端或 Codex 已授予屏幕录制权限。"
        case .contactNotFound(let contact):
            return "未在轻推搜索结果中找到精确匹配联系人：\(contact)"
        case .openedWrongChat(let expected, let actual):
            return "打开的会话不是目标联系人，期望“\(expected)”，实际“\(actual)”。"
        case .messageDraftFailed(let detail):
            return "消息草稿写入失败：\(detail)"
        case .messageNotSent(let detail):
            return "消息未成功发送：\(detail)"
        }
    }
}

func printUsage() {
    let text = """
    用法:
      swift scripts/send_qingtui_message.swift --contact "<联系人>" --message "<消息>" [--dry-run] [--timeout 12]

    参数:
      --contact   轻推联系人显示名，必须精确匹配
      --message   要发送的文本内容
      --dry-run   只打开并校验会话，不发送消息
      --timeout   超时时间，默认 12 秒
    """
    print(text)
}

func parseArguments() throws -> Options {
    let args = Array(CommandLine.arguments.dropFirst())
    if args.isEmpty || args.contains("--help") || args.contains("-h") {
        throw ScriptError.usage("")
    }

    var contact: String?
    var message: String?
    var dryRun = false
    var timeout: TimeInterval = 12

    var index = 0
    while index < args.count {
        let arg = args[index]
        switch arg {
        case "--contact":
            index += 1
            guard index < args.count else {
                throw ScriptError.usage("缺少 --contact 的值")
            }
            contact = args[index]
        case "--message":
            index += 1
            guard index < args.count else {
                throw ScriptError.usage("缺少 --message 的值")
            }
            message = args[index]
        case "--timeout":
            index += 1
            guard index < args.count, let value = Double(args[index]), value > 0 else {
                throw ScriptError.usage("--timeout 必须是正数")
            }
            timeout = value
        case "--dry-run":
            dryRun = true
        default:
            throw ScriptError.usage("未知参数：\(arg)")
        }
        index += 1
    }

    guard let contact, !contact.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
        throw ScriptError.usage("contact 不能为空")
    }
    guard let message, !message.isEmpty else {
        throw ScriptError.usage("message 不能为空")
    }

    return Options(
        contact: contact.trimmingCharacters(in: .whitespacesAndNewlines),
        message: message,
        dryRun: dryRun,
        timeout: timeout
    )
}

func sleepBriefly(_ seconds: TimeInterval) {
    usleep(useconds_t(seconds * 1_000_000))
}

func waitUntil<T>(
    timeout: TimeInterval,
    interval: TimeInterval = 0.2,
    _ condition: () -> T?
) -> T? {
    let deadline = Date().addingTimeInterval(timeout)
    while Date() < deadline {
        if let result = condition() {
            return result
        }
        sleepBriefly(interval)
    }
    return nil
}

func runProcess(_ launchPath: String, _ arguments: [String]) -> Int32 {
    let task = Process()
    task.executableURL = URL(fileURLWithPath: launchPath)
    task.arguments = arguments
    do {
        try task.run()
        task.waitUntilExit()
        return task.terminationStatus
    } catch {
        return -1
    }
}

func runningQingTuiApp() -> NSRunningApplication? {
    NSWorkspace.shared.runningApplications.first {
        $0.bundleIdentifier == qingtuiBundleID || $0.localizedName == qingtuiAppName
    }
}

func firstInstalledQingTuiPath() -> String? {
    if let url = NSWorkspace.shared.urlForApplication(withBundleIdentifier: qingtuiBundleID) {
        return url.path
    }

    let task = Process()
    let pipe = Pipe()
    task.executableURL = URL(fileURLWithPath: "/usr/bin/mdfind")
    task.arguments = [
        "kMDItemKind == \"Application\" && (kMDItemDisplayName == \"轻推\" || kMDItemFSName == \"轻推.app\" || kMDItemCFBundleIdentifier == \"\(qingtuiBundleID)\")"
    ]
    task.standardOutput = pipe
    do {
        try task.run()
        task.waitUntilExit()
    } catch {
        return nil
    }

    guard task.terminationStatus == 0 else {
        return nil
    }
    let data = pipe.fileHandleForReading.readDataToEndOfFile()
    let output = String(decoding: data, as: UTF8.self)
    return output
        .split(separator: "\n")
        .map(String.init)
        .first(where: { !$0.isEmpty })
}

func ensureQingTuiRunning(timeout: TimeInterval) throws -> NSRunningApplication {
    if let app = runningQingTuiApp() {
        return app
    }

    guard let appPath = firstInstalledQingTuiPath() else {
        throw ScriptError.qingtuiNotInstalled
    }

    let status = runProcess("/usr/bin/open", [appPath])
    guard status == 0 else {
        throw ScriptError.qingtuiLaunchFailed
    }

    guard let app = waitUntil(timeout: timeout, { runningQingTuiApp() }) else {
        throw ScriptError.qingtuiLaunchFailed
    }
    return app
}

func axValue(_ element: UIElement, _ attribute: String) -> AnyObject? {
    var value: CFTypeRef?
    let result = AXUIElementCopyAttributeValue(element, attribute as CFString, &value)
    guard result == .success else {
        return nil
    }
    return value
}

func axChildren(_ element: UIElement) -> [UIElement] {
    axValue(element, kAXChildrenAttribute as String) as? [UIElement] ?? []
}

func axCGRect(_ element: UIElement) -> CGRect? {
    guard
        let positionRef = axValue(element, kAXPositionAttribute as String),
        let sizeRef = axValue(element, kAXSizeAttribute as String)
    else {
        return nil
    }

    var point = CGPoint.zero
    var size = CGSize.zero
    guard
        AXValueGetValue(positionRef as! AXValue, .cgPoint, &point),
        AXValueGetValue(sizeRef as! AXValue, .cgSize, &size)
    else {
        return nil
    }

    return CGRect(origin: point, size: size)
}

func mainWindow(app: NSRunningApplication) -> UIElement? {
    let axApp = AXUIElementCreateApplication(app.processIdentifier)
    let windows = axValue(axApp, kAXWindowsAttribute as String) as? [UIElement] ?? []

    return windows
        .compactMap { window -> (UIElement, CGRect)? in
            guard let bounds = axCGRect(window), bounds.width > 700, bounds.height > 500 else {
                return nil
            }
            return (window, bounds)
        }
        .sorted { lhs, rhs in
            (lhs.1.width * lhs.1.height) > (rhs.1.width * rhs.1.height)
        }
        .first?
        .0
}

func windowBounds(app: NSRunningApplication) -> CGRect? {
    guard let window = mainWindow(app: app) else {
        return nil
    }
    return axCGRect(window)
}

func keyPress(_ keyCode: CGKeyCode, flags: CGEventFlags = []) {
    let source = CGEventSource(stateID: .hidSystemState)
    let keyDown = CGEvent(keyboardEventSource: source, virtualKey: keyCode, keyDown: true)
    keyDown?.flags = flags
    keyDown?.post(tap: .cghidEventTap)

    let keyUp = CGEvent(keyboardEventSource: source, virtualKey: keyCode, keyDown: false)
    keyUp?.flags = flags
    keyUp?.post(tap: .cghidEventTap)
}

func click(at point: CGPoint) {
    let source = CGEventSource(stateID: .hidSystemState)
    let down = CGEvent(mouseEventSource: source, mouseType: .leftMouseDown, mouseCursorPosition: point, mouseButton: .left)
    down?.post(tap: .cghidEventTap)
    usleep(50_000)
    let up = CGEvent(mouseEventSource: source, mouseType: .leftMouseUp, mouseCursorPosition: point, mouseButton: .left)
    up?.post(tap: .cghidEventTap)
}

func withTemporaryClipboard(_ text: String, body: () -> Void) {
    let pasteboard = NSPasteboard.general
    let originalText = pasteboard.string(forType: .string)

    pasteboard.clearContents()
    pasteboard.setString(text, forType: .string)
    body()
    sleepBriefly(0.15)

    pasteboard.clearContents()
    if let originalText {
        pasteboard.setString(originalText, forType: .string)
    }
}

func screenshot(of bounds: CGRect, name: String) throws -> URL {
    let path = URL(fileURLWithPath: NSTemporaryDirectory()).appendingPathComponent(name)
    try? FileManager.default.removeItem(at: path)

    let rect = "\(Int(bounds.minX)),\(Int(bounds.minY)),\(Int(bounds.width)),\(Int(bounds.height))"
    let status = runProcess("/usr/sbin/screencapture", ["-x", "-R\(rect)", path.path])
    guard status == 0, FileManager.default.fileExists(atPath: path.path) else {
        throw ScriptError.screenCaptureFailed
    }
    return path
}

func recognizeText(in imageURL: URL) throws -> [OCRText] {
    guard let image = NSImage(contentsOf: imageURL) else {
        return []
    }
    var rect = NSRect(origin: .zero, size: image.size)
    guard let cgImage = image.cgImage(forProposedRect: &rect, context: nil, hints: nil) else {
        return []
    }

    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.recognitionLanguages = ["zh-Hans", "en-US"]
    request.usesLanguageCorrection = true

    let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    try handler.perform([request])

    return (request.results ?? []).compactMap { observation in
        guard let candidate = observation.topCandidates(1).first else {
            return nil
        }
        return OCRText(text: candidate.string, box: observation.boundingBox)
    }
}

func normalize(_ text: String) -> String {
    text
        .replacingOccurrences(of: "\n", with: " ")
        .replacingOccurrences(of: "\t", with: " ")
        .replacingOccurrences(of: "\u{00A0}", with: " ")
        .split(whereSeparator: \.isWhitespace)
        .joined(separator: " ")
        .trimmingCharacters(in: .whitespacesAndNewlines)
}

func prefixMatches(_ recognizedText: String, contact: String) -> Bool {
    let text = normalize(recognizedText)
    let target = normalize(contact)
    return text == target
        || text.hasPrefix(target + " ")
        || text.hasPrefix(target + ",")
        || text.hasPrefix(target + "，")
}

func verificationToken(for message: String) -> String {
    let normalized = normalize(message)
    return String(normalized.prefix(min(16, normalized.count)))
}

func windowPoint(relativeX: CGFloat, relativeYFromTop: CGFloat, in bounds: CGRect) -> CGPoint {
    CGPoint(
        x: bounds.minX + bounds.width * relativeX,
        y: bounds.minY + bounds.height * relativeYFromTop
    )
}

func windowPoint(for OCRBox: CGRect, in bounds: CGRect) -> CGPoint {
    CGPoint(
        x: bounds.minX + bounds.width * OCRBox.midX,
        y: bounds.minY + bounds.height * (1 - OCRBox.midY)
    )
}

func firstSearchResult(for contact: String, in texts: [OCRText]) -> OCRText? {
    texts
        .filter {
            prefixMatches($0.text, contact: contact)
                && $0.midX < 0.35
                && $0.midY > 0.65
                && $0.midY < 0.9
        }
        .sorted { lhs, rhs in lhs.midY > rhs.midY }
        .first
}

func headerMatch(for contact: String, in texts: [OCRText]) -> OCRText? {
    texts
        .filter {
            normalize($0.text) == normalize(contact)
                && $0.midX > 0.25
                && $0.midX < 0.6
                && $0.midY > 0.72
        }
        .sorted { lhs, rhs in lhs.midY > rhs.midY }
        .first
}

func guessedHeader(in texts: [OCRText]) -> String {
    texts
        .filter { $0.midX > 0.25 && $0.midX < 0.6 && $0.midY > 0.72 }
        .map(\.text)
        .map(normalize)
        .first(where: { !$0.isEmpty }) ?? "未知"
}

func hasDraftMessage(token: String, in texts: [OCRText]) -> Bool {
    texts.contains {
        normalize($0.text).contains(token)
            && $0.midX > 0.3
            && $0.midY < 0.22
    }
}

func hasSentMessage(token: String, in texts: [OCRText]) -> Bool {
    texts.contains {
        normalize($0.text).contains(token)
            && $0.midX > 0.65
            && $0.midY > 0.12
            && $0.midY < 0.45
    }
}

func refreshWindowBounds(app: NSRunningApplication, timeout: TimeInterval) throws -> CGRect {
    guard let bounds = waitUntil(timeout: timeout, { windowBounds(app: app) }) else {
        throw ScriptError.chatWindowNotFound
    }
    return bounds
}

func openChat(contact: String, app: NSRunningApplication, timeout: TimeInterval) throws {
    let bounds = try refreshWindowBounds(app: app, timeout: timeout)

    click(at: windowPoint(relativeX: 0.15, relativeYFromTop: 0.09, in: bounds))
    sleepBriefly(0.35)

    withTemporaryClipboard(contact) {
        keyPress(0, flags: .maskCommand)
        sleepBriefly(0.08)
        keyPress(51)
        sleepBriefly(0.08)
        keyPress(9, flags: .maskCommand)
    }

    sleepBriefly(0.9)

    let searchShot = try screenshot(of: bounds, name: "qingtui-search-\(UUID().uuidString).png")
    let searchTexts = try recognizeText(in: searchShot)
    guard let result = firstSearchResult(for: contact, in: searchTexts) else {
        throw ScriptError.contactNotFound(contact)
    }

    click(at: windowPoint(for: result.box, in: bounds))
    sleepBriefly(1.0)

    let chatShot = try screenshot(of: bounds, name: "qingtui-chat-\(UUID().uuidString).png")
    let chatTexts = try recognizeText(in: chatShot)
    guard headerMatch(for: contact, in: chatTexts) != nil else {
        throw ScriptError.openedWrongChat(expected: contact, actual: guessedHeader(in: chatTexts))
    }
}

func sendMessage(_ message: String, app: NSRunningApplication, timeout: TimeInterval) throws {
    let bounds = try refreshWindowBounds(app: app, timeout: timeout)
    let token = verificationToken(for: message)

    click(at: windowPoint(relativeX: 0.48, relativeYFromTop: 0.93, in: bounds))
    sleepBriefly(0.2)

    withTemporaryClipboard(message) {
        keyPress(0, flags: .maskCommand)
        sleepBriefly(0.08)
        keyPress(51)
        sleepBriefly(0.08)
        keyPress(9, flags: .maskCommand)
    }

    sleepBriefly(0.6)

    let draftShot = try screenshot(of: bounds, name: "qingtui-draft-\(UUID().uuidString).png")
    let draftTexts = try recognizeText(in: draftShot)
    guard hasDraftMessage(token: token, in: draftTexts) else {
        throw ScriptError.messageDraftFailed("未在输入区检测到消息草稿")
    }

    keyPress(36)
    sleepBriefly(1.0)

    let sentShot = try screenshot(of: bounds, name: "qingtui-sent-\(UUID().uuidString).png")
    let sentTexts = try recognizeText(in: sentShot)
    guard hasSentMessage(token: token, in: sentTexts) else {
        throw ScriptError.messageNotSent("发送后未在右侧会话区检测到消息气泡")
    }
}

func run() throws {
    let options = try parseArguments()

    if !AXIsProcessTrusted() {
        throw ScriptError.missingAccessibilityPermission
    }

    let app = try ensureQingTuiRunning(timeout: options.timeout)
    _ = app.activate(options: [.activateAllWindows])
    sleepBriefly(0.8)

    _ = try refreshWindowBounds(app: app, timeout: options.timeout)
    try openChat(contact: options.contact, app: app, timeout: options.timeout)

    if options.dryRun {
        print("dry-run ok: \(options.contact)")
        return
    }

    try sendMessage(options.message, app: app, timeout: options.timeout)
    print("sent: \(options.contact)")
}

do {
    try run()
} catch let error as ScriptError {
    if case .usage(let detail) = error, detail.isEmpty {
        printUsage()
        exit(0)
    }
    fputs("ERROR: \(error.localizedDescription)\n", stderr)
    if case .usage = error {
        printUsage()
    }
    exit(1)
} catch {
    fputs("ERROR: \(error.localizedDescription)\n", stderr)
    exit(1)
}
