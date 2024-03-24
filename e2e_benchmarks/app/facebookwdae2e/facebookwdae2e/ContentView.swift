//
//  ContentView.swift
//  facebookwdae2e
//
//  Created by youngfreefjs on 2024/3/20.
//

import SwiftUI

// Custom struct to encapsulate the confirmation alert logic with a button
struct ConfirmationAlertButton: View {
    @Binding var isPresented: Bool
    let id: String
    
    var body: some View {
        Button(id) {
            isPresented = true
        }
        .id(id)
        .accessibilityLabel(id)
        .accessibilityIdentifier(id)
        .alert(isPresented: $isPresented) {
            Alert(
                title: Text("Confirmation"),
                message: Text("Do you accept?"),
                primaryButton: .default(Text("Accept").accessibilityLabel("Accept")) {
                    // Handle acceptance
                    print("Accepted")
                },
                secondaryButton: .cancel(Text("Reject").accessibilityLabel("Reject")) {
                    // Handle rejection
                    print("Rejected")
                }
            )
        }
        .padding()
    }
}

// Custom struct to encapsulate the text input alert logic
struct TextInputAlert: View {
    @Binding var isPresented: Bool
    @Binding var text: String
    let onAccept: (String) -> Void
    
    var body: some View {
        if isPresented {
            VStack(spacing: 20) {
                Text("Enter your input")
                TextField("Enter text", text: $text)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                HStack(spacing: 20) {
                    Button("Cancel") {
                        isPresented = false
                    }
                    Button("Accept") {
                        isPresented = false
                        onAccept(text)
                    }
                }
            }
            .padding()
            .background(Color.white)
            .cornerRadius(10)
            .shadow(radius: 5)
            .frame(maxWidth: 300)
            .transition(.scale)
        }
    }
}

// View extension to present the custom text input alert
extension View {
    func textInputAlert(isPresented: Binding<Bool>, text: Binding<String>, onAccept: @escaping (String) -> Void) -> some View {
        ZStack {
            self
            TextInputAlert(isPresented: isPresented, text: text, onAccept: onAccept)
                .animation(.default, value: isPresented.wrappedValue)
                .opacity(isPresented.wrappedValue ? 1 : 0)
        }
    }
}

// ContentView using both ConfirmationAlertButton and TextInputAlert
struct ContentView: View {
    @State private var showConfirmationAlert = false
    @State private var showTextInputAlert = false
    @State private var userInput = "this value"
    @State private var isButtonHidden = true
    @State private var isChecked: Bool = false
    @State private var inputText: String = ""
    @State private var longTapShowAlert = false
    @State private var DoubleTapShowAlert = false
    @State private var showAlert = false
    @State private var alertText = ""
    @State private var orientation: UIDeviceOrientation = UIDevice.current.orientation


    let acceptOrRejectAlertID = "ACCEPT_OR_REJECT_ALERT"
    let inputAlertID = "INPUT_ALERT"
    
    
    var orientationText: String {
        switch orientation {
        case .landscapeLeft, .landscapeRight:
            return "LANDSCAPE"
        case .portrait, .portraitUpsideDown:
            return "PORTRAIT"
        default:
            return "UNKNOW"
        }
    }
    
    var body: some View {
        NavigationView {
            
            VStack {
                
                HStack {
                    ConfirmationAlertButton(isPresented: $showConfirmationAlert, id: acceptOrRejectAlertID)
                    
                    Button(inputAlertID) {
                        showTextInputAlert = true
                    }.id(inputAlertID)
                        .accessibilityLabel(inputAlertID)
                        .accessibilityIdentifier(inputAlertID)
                        .padding()
                    
                
                }
                
                // 新的并排按钮
                HStack {
                    // 启用的按钮
                    Button("ENABLED_BTN") {
                        // 这里处理按钮点击事件
                        print("Enabled button tapped")
                    }
                    .background(Color.black) // 背景颜色
                    .accessibilityLabel("ENABLED_BTN")
                    .accessibilityIdentifier("ENABLED_BTN")
                    
                    .padding()
                    
                    // 禁用的按钮
                    Button("DISABLED_BTN") {
                        // 由于按钮被禁用，这里的代码不会被执行
                    }
                    .accessibilityLabel("DISABLED_BTN")
                    .accessibilityIdentifier("DISABLED_BTN")
                    .disabled(true) // 禁用按钮
                    .padding()
                    
                    // 添加本地图像
                    Image("applogo")
                        .resizable()
                        .scaledToFit()
                        .frame(width: 100, height: 50)
                        .accessibilityIdentifier("IMG_BTN")
                    
                    // 隐藏按钮
                    Button("HIDDEN_BTN") {
                        // 按钮的动作
                    }
                    .opacity(isButtonHidden ? 0 : 1) // 根据条件设置透明度
                    // 或者
                    //                 .hidden(isButtonHidden) // 根据条件隐藏按钮，但这需要自定义扩展
                }
                
                // select
                HStack {
                    // 没有被选中的勾选框
                    Button(action: {
                        isChecked = false
                    }) {
                        Image(systemName: isChecked ? "circle" : "checkmark.circle.fill")
                    }.accessibilityIdentifier("CHECKED_BTN")
                    
                    // 被选中的勾选框
                    Button(action: {
                        isChecked = true
                    }) {
                        Image(systemName: isChecked ? "checkmark.circle.fill" : "circle")
                    }.accessibilityIdentifier("UNCHECKED_BTN")
                }
                // input
                HStack {
                    TextField("INPUT_FIELD", text: $inputText)
                        .accessibilityLabel("INPUT_FIELD")
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .padding()
                    
                    Button(action: {
                        self.inputText = "" // 清空输入框
                    }) {
                        Text("CLEAR INPUT")
                    }.accessibilityLabel("CLEAR_INPUT_BTN")
                        .padding()
                }
                
                // accessibilityContainer COMBINED_TEXT_CONTAINER
                VStack {
                    Text("First line of text")
                    Text("Second line of text")
                    Text("Third line of text")
                }
                .accessibilityElement(children: .combine)
                .accessibilityIdentifier("COMBINED_TEXT_CONTAINER")
                
                HStack {
                    Text("LONG_TAP_ALERT")
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(Color.white)
                    .cornerRadius(5)
                    .onLongPressGesture(minimumDuration: 1.0) {
                        self.longTapShowAlert = true
                    }
                    .alert(isPresented: $longTapShowAlert) {
                        Alert(
                            title: Text("Long Tap Alert"),
                            message: Text("Long Tap Alert"),
                            dismissButton: .default(Text("LONG_TAP_ALERT_OK"))
                        )
                    }
                    
                    Text("DOUBLE_TAP_ALERT")
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(Color.white)
                    .cornerRadius(5)
                    .onTapGesture(count: 2) {
                        self.DoubleTapShowAlert = true
                    }
                    .alert(isPresented: $DoubleTapShowAlert) {
                        Alert(
                            title: Text("DOUBLE Tap Alert"),
                            message: Text("DOUBLE Tap Alert"),
                            dismissButton: .default(Text("DOUBLE_TAP_ALERT_OK"))
                        )
                    }
                    
                    
                }
                
                // Return Origatation Text
                Text(orientationText)
                .accessibilityIdentifier("ORIGATATION_TEXT")
                .onAppear {
                    // Listener
                    NotificationCenter.default.addObserver(
                        forName: UIDevice.orientationDidChangeNotification,
                        object: nil,
                        queue: .main
                    ) { _ in
                        // Update
                        orientation = UIDevice.current.orientation
                    }
                }
                
                
                
                // List View
                HStack {
                    // GO OTHER
                    NavigationLink(destination: ListView()) {
                        Text("ListView")
                    }
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(Color.white)
                    .cornerRadius(8)
                    
                    // GO LIST
                    NavigationLink(destination: DragView()) {
                        Text("DragView")
                    }
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(Color.white)
                    .cornerRadius(8)
                    
                    // 其他内容
                }
                .navigationBarTitle("Home", displayMode: .inline)
                
            }
            .textInputAlert(isPresented: $showTextInputAlert, text: $userInput) { enteredText in
                // Handle the text input acceptance here
                print("The user entered: \(enteredText)")
            }
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}


// SwiftUI 没有内置的带文本输入的弹出对话框，所以我们需要自定义一个
extension View {
    func textFieldAlert(isPresented: Binding<Bool>, text: Binding<String>) -> some View {
        TextFieldAlert(isPresented: isPresented, text: text, presentingView: self)
    }
}

struct TextFieldAlert<PresentingView: View>: UIViewControllerRepresentable {
    @Binding var isPresented: Bool
    @Binding var text: String
    let presentingView: PresentingView
    
    func makeUIViewController(context: Context) -> UIViewController {
        UIViewController()
    }
    
    func updateUIViewController(_ uiViewController: UIViewController, context: Context) {
        guard context.coordinator.alert == nil else { return }
        
        if isPresented {
            let alert = UIAlertController(title: "Alert", message: "Type something:", preferredStyle: .alert)
            alert.addTextField { textField in
                textField.placeholder = "Enter text here"
                textField.text = text
            }
            
            alert.addAction(UIAlertAction(title: "Submit", style: .default) { _ in
                if let textField = alert.textFields?.first, let text = textField.text {
                    self.text = text
                    isPresented = false
                }
            })
            
            alert.addAction(UIAlertAction(title: "Cancel", style: .cancel) { _ in
                isPresented = false
            })
            
            context.coordinator.alert = alert
            
            DispatchQueue.main.async { // Must be presented in the main thread
                uiViewController.present(alert, animated: true, completion: {
                    self.isPresented = false
                    context.coordinator.alert = nil
                })
            }
        }
    }
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
    
    class Coordinator {
        var alert: UIAlertController?
        var textFieldAlert: TextFieldAlert
        
        init(_ textFieldAlert: TextFieldAlert) {
            self.textFieldAlert = textFieldAlert
        }
    }
}
