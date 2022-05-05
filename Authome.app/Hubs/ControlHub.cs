using Microsoft.AspNetCore.SignalR;

namespace AutHome.Hubs;

public class ControlHub : Hub
{
	public async Task SendLivingRoomTemperature(int temperature)
	{
		await Clients.All.SendAsync("Temperature", temperature);
	}

	public async Task SendLivingRoomHumidity(int humidity)
	{
		await Clients.All.SendAsync("Humidity", humidity);
	}
}