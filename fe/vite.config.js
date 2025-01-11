export default ({
server: {
	host: 'localhost', // Or your actual host name
	hmr: {
		host: 'localhost', // Ensure this matches your host, can be your ip address if testing on your network
		clientPort: 8081 //the port used by the ws server
	},
  },
// ... other config
});