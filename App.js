import { Image, StyleSheet, View } from "react-native"
import useSocket from "./hooks/useSocket"
import { useEffect, useState } from "react"
import WebView from "react-native-webview"

export default function App() {
	const socket = useSocket()
	const [image, setImage] = useState()

	useEffect(() => {
		if (socket) {
			socket.emit("start_stream")

			socket.on("video_frame", (b64) => {
				setImage(b64)
			})

			return () => socket.disconnect()
		}
	}, [socket])

	return (
		<View style={styles.container}>
			{image && (
				<WebView
					source={{ uri: `data:image/jpeg;base64,${image}` }}
					style={styles.image}
				/>
			)}
		</View>
	)
}

const styles = StyleSheet.create({
	container: {
		flex: 1,
		backgroundColor: "#fff",
		alignItems: "center",
		justifyContent: "center",
	},
	image: {
		width: 360,
		height: 240,
	},
})
