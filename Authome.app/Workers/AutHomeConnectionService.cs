using Microsoft.AspNetCore.SignalR.Client;
using AutHome.Data;
using Microsoft.AspNetCore.SignalR;
using AutHome.Hubs;
using MQTTnet;
using MQTTnet.Client.Options;
using MQTTnet.Client;
using MQTTnet.Client.Subscribing;
using MQTTnet.Client.Receiving;

namespace AutHome.Workers;

public class AutHomeConnectionService : IHostedService, IDisposable
{
	private readonly ILogger<AutHomeConnectionService> _logger;
	private readonly IHubContext<ControlHub> _hub;
	private readonly IMqttClient client;

	public AutHomeConnectionService(ILogger<AutHomeConnectionService> logger, IHubContext<ControlHub> hub)
	{
		_logger = logger;
		_hub = hub;
		var factory = new MqttFactory();
		client = factory.CreateMqttClient();
		
	}

	public async Task StartAsync(CancellationToken cancellationToken)
	{
		var mqttClientOptions = new MqttClientOptionsBuilder().WithTcpServer("localhost").Build();
		await client.ConnectAsync(mqttClientOptions, cancellationToken);
		_logger.LogInformation("Connected to MQTT broker.");
		await client.SubscribeAsync("authome/#");
		client.ApplicationMessageReceivedHandler = new TestHandler(_logger, _hub);
	}

	public async Task StopAsync(CancellationToken cancellationToken)
	{
		await client!.DisconnectAsync(cancellationToken);
		_logger.LogInformation("Disconnected from MQTT broker.");
	}

	public void Dispose()
	{
		client!.Dispose();
	}
}

public class TestHandler : IMqttApplicationMessageReceivedHandler
{
	private readonly ILogger<AutHomeConnectionService> _logger;
	private readonly IHubContext<ControlHub> _hub;

	public TestHandler(ILogger<AutHomeConnectionService> logger, IHubContext<ControlHub> hub)
	{
		_logger = logger;
		_hub = hub;
	}

	public async Task HandleApplicationMessageReceivedAsync(MqttApplicationMessageReceivedEventArgs eventArgs)
	{
		switch (eventArgs.ApplicationMessage.Topic)
		{
			case "authome/system/status":
				break;
			case "authome/room/kitchen/light":
				break;
			case "authome/room/livingroom/light":
				break;
			case "authome/room/bedroom/light":
				break;
			case "authome/room/bedroom/temperature":
				await _hub.Clients.All.SendAsync("Temperature", int.Parse(eventArgs.ApplicationMessage.ConvertPayloadToString()));
				break;
			case "authome/room/bedroom/humidity":
				await _hub.Clients.All.SendAsync("Humidity", int.Parse(eventArgs.ApplicationMessage.ConvertPayloadToString()));
				break;
			case "authome/security/door/front" :
				break;
			default:
				break;
		}
	}
}