import Foundation

struct SearchResult: Identifiable, Decodable {
    var id: String
    var similarity: Double
    var file_name: String
    var file_path: String
    var media_category: String
    var description: String
    var mime_type: String
    var preview: String
    var timestamp: String
    var source: String
}

struct IngestResult: Decodable {
    var status: String
    var id: String?
    var path: String?
    var category: String?
    var reason: String?
    var error: String?
}
