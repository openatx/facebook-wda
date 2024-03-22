//
//  DragView.swift
//  facebookwdae2e
//
//  Created by youngfreefjs on 2024/3/21.
//

import Foundation
import SwiftUI

struct DragView: View {
    @State private var showingAlert = false
    @State private var isLongPressing = false
    
    // 按钮B的布局边界
    @State private var buttonBFrame: CGRect = .zero

    var body: some View {
        VStack {
            // 按钮A
            Button("按钮 A (长按并拖到B)") {
                // 不在这里处理点击事件
            }
            .simultaneousGesture(LongPressGesture(minimumDuration: 0.5).onEnded { _ in
                self.isLongPressing = true
            })
            .gesture(DragGesture(minimumDistance: 0)
                .onEnded { value in
                    if self.isLongPressing && self.buttonBFrame.contains(value.location) {
                        self.showingAlert = true
                    }
                    self.isLongPressing = false
                }
            )

            Spacer().frame(height: 50)

            // 按钮B
            Button("按钮 B") {
                // 不在这里处理点击事件
            }
            .background(GeometryReader { geometry in
                Color.clear.onAppear { self.buttonBFrame = geometry.frame(in: .global) }
            })

            Spacer()
        }
        .alert(isPresented: $showingAlert) {
            Alert(title: Text("成功"), message: Text("你已经成功长按并拖动到按钮 B！"), dismissButton: .default(Text("好的")))
        }
    }
}
