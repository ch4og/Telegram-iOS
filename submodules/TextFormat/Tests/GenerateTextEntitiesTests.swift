import XCTest
import TelegramCore
@testable import TextFormat

final class GenerateTextEntitiesTests: XCTestCase {
    func testMentionIsNotDetectedInsideEmailAddress() {
        let entities = generateTextEntities("me@alex.com", enabledTypes: [.internalUrl, .mention])
        XCTAssertFalse(entities.contains(where: { entity in
            if case .Mention = entity.type {
                return true
            } else {
                return false
            }
        }))
    }

    func testMentionIsDetectedAfterWhitespace() {
        let entities = generateTextEntities("contact @alex", enabledTypes: [.mention])
        XCTAssertEqual(entities, [MessageTextEntity(range: 8 ..< 13, type: .Mention)])
    }

    func testMentionIsDetectedAfterOpeningParenthesis() {
        let entities = generateTextEntities("(@alex)", enabledTypes: [.mention])
        XCTAssertEqual(entities, [MessageTextEntity(range: 1 ..< 6, type: .Mention)])
    }

    func testMentionIsNotDetectedAfterPunctuation() {
        let entities = generateTextEntities("contact,@alex", enabledTypes: [.mention])
        XCTAssertFalse(entities.contains(where: { entity in
            if case .Mention = entity.type {
                return true
            } else {
                return false
            }
        }))
    }
}
