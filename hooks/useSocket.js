import { io } from "socket.io-client"
import { useEffect, useState } from "react"
import { SOCKET_SERVER_URI } from "../constants"

export default function useSocket() {
	const [socket, setSocket] = useState()

	useEffect(() => {
		setSocket(io(SOCKET_SERVER_URI))
	}, [])

	return socket
}
