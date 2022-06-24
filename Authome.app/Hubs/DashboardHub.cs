using AutHome.Services;

using Microsoft.AspNetCore.SignalR;

namespace AutHome.Hubs;

public class DashboardHub : Hub
{
	public async Task GetCurrentStatus()
	{
		await Clients.Caller.SendAsync("MCUStatus", MQTTConnectionService.MCUStatus);
		await Clients.Caller.SendAsync("MCUTemperature", MQTTConnectionService.MCUTemperature);
		await Clients.Caller.SendAsync("DHTTemperature", MQTTConnectionService.DHTTemperature);
		await Clients.Caller.SendAsync("DHTHumidity", MQTTConnectionService.DHTHumidity);
		await Clients.Caller.SendAsync("Relay1State", MQTTConnectionService.Relay1State);
		await Clients.Caller.SendAsync("Relay2State", MQTTConnectionService.Relay2State);
		await Clients.Caller.SendAsync("Relay3State", MQTTConnectionService.Relay3State);
	}
}
