import Foundation
import Vision
import AppKit

func recognizeText(at path: String) throws -> String {
    let url = URL(fileURLWithPath: path)
    guard let image = NSImage(contentsOf: url) else {
        throw NSError(domain: "ocr", code: 1, userInfo: [NSLocalizedDescriptionKey: "load image failed"])
    }

    var rect = NSRect(origin: .zero, size: image.size)
    guard let cgImage = image.cgImage(forProposedRect: &rect, context: nil, hints: nil) else {
        throw NSError(domain: "ocr", code: 2, userInfo: [NSLocalizedDescriptionKey: "cgimage failed"])
    }

    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true
    request.recognitionLanguages = ["zh-Hans", "en-US"]

    let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    try handler.perform([request])

    let lines = (request.results ?? [])
        .compactMap { $0.topCandidates(1).first?.string.trimmingCharacters(in: .whitespacesAndNewlines) }
        .filter { !$0.isEmpty }
    return lines.joined(separator: "\n")
}

do {
    let args = Array(CommandLine.arguments.dropFirst())
    guard let imagePath = args.first else {
        fputs("usage: ocr_vision <image-path>\n", stderr)
        exit(2)
    }

    print(try recognizeText(at: imagePath))
} catch {
    fputs("OCR failed: \(error)\n", stderr)
    exit(1)
}
