import { io } from "socket.io-client"
import { useEffect, useState } from "react"

const SOCKET_SERVER_URI = "http://192.168.2.165:8000"

export default function useSocket() {
	const [socket, setSocket] = useState()

	useEffect(() => {
		setSocket(io(SOCKET_SERVER_URI))
	}, [])

	return socket
}
