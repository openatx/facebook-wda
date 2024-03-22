//
//  ListView.swift
//  facebookwdae2e
//
//  Created by youngfreefjs on 2024/3/21.
//

import Foundation
import SwiftUI

// ListView.swift
struct ListView: View {
    var body: some View {
        List(1...100, id: \.self) { number in
            Text("Row\(number)")
        }.accessibilityLabel("LIST_CONTAINER")
        .navigationBarTitle("Numbers List", displayMode: .inline)
    }
}
