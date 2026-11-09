import Foundation
import FoundationModels

guard case .available = SystemLanguageModel.default.availability else {
    FileHandle.standardError.write(Data("Local model: \(SystemLanguageModel.default.availability)\n".utf8))
    exit(2)
}
let input = FileHandle.standardInput.readDataToEndOfFile()
let prompt = String(decoding: input, as: UTF8.self)
let session = LanguageModelSession()
let seed = UInt64(CommandLine.arguments.dropFirst().first ?? "0") ?? 0
let options = GenerationOptions(sampling: .random(top: 16, seed: seed), temperature: 0.6, maximumResponseTokens: 192)
let response = try await session.respond(to: prompt, options: options)
print(response.content)
