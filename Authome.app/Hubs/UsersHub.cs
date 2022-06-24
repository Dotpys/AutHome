using Microsoft.AspNetCore.SignalR;

namespace AutHome.Hubs;

public class UsersHub : Hub
{
	public async Task Update()
	{
		await Clients.All.SendAsync("Update");
	}
}
