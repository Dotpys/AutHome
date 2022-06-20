using Microsoft.AspNetCore.SignalR.Client;
using Microsoft.AspNetCore.SignalR;
using AutHome.Hubs;
using MQTTnet;
using MQTTnet.Client;
using MQTTnet.Exceptions;
using System.Text.RegularExpressions;
using AutHome.Data;
using System.Text;

namespace AutHome.Services;

public class MQTTConnectionService : IHostedService, IDisposable
{
	private readonly IConfiguration _configuration;
	private readonly ILogger<MQTTConnectionService> _logger;
	private readonly IHubContext<ControlHub> _hub;
	private readonly FingerprintImageStore _imageStore;

	private readonly MqttFactory _mqttFactory;
	private readonly IMqttClient _mqttClient;
	private readonly MqttClientOptions _mqttClientOptions;
	Regex reg = new(@"authome\/user\/(?<userId>[0-9A-F]{32})\/(?<property>(image|characteristics|index))");

	public bool IsConnected { get => _mqttClient.IsConnected; }

	public MQTTConnectionService(
		IConfiguration mqttConfiguration,
		ILogger<MQTTConnectionService> logger,
		IHubContext<ControlHub> hub,
		FingerprintImageStore imageStore)
	{
		_configuration = mqttConfiguration;
		_logger = logger;
		_hub = hub;
		_imageStore = imageStore;

		_mqttFactory = new();
		_mqttClient = _mqttFactory.CreateMqttClient();
		string host = _configuration.GetValue("MQTT:Broker:Address", "localhost");
		int port = _configuration.GetValue("MQTT:Broker:Port", 1883);
		_mqttClientOptions = new MqttClientOptionsBuilder()
			.WithTcpServer(host, port)
			.WithClientId(_configuration.GetValue("MQTT:ClientId", "Backend-Client"))
			.Build();
	}

	public async Task StartAsync(CancellationToken cancellationToken)
	{
		MqttClientConnectResult connectionResult = await _mqttClient.ConnectAsync(_mqttClientOptions, cancellationToken);
		_logger.LogInformation("Connected to MQTT broker.");
		await _mqttClient.SubscribeAsync("authome/#");
		_mqttClient.ApplicationMessageReceivedAsync += MessageReceived;
	}

	public async Task StopAsync(CancellationToken cancellationToken)
	{
		await _mqttClient!.DisconnectAsync(new() { Reason= MqttClientDisconnectReason.NormalDisconnection}, cancellationToken);
		_logger.LogInformation("Disconnected from MQTT broker.");
	}

	public void Dispose()
	{
		_mqttClient!.Dispose();
	}

	private async Task MessageReceived(MqttApplicationMessageReceivedEventArgs eventArgs)
	{
		switch (eventArgs.ApplicationMessage.Topic)
		{
			case "authome/mcu/temperature":
				await _hub.Clients.All.SendAsync("MicrocontrollerTemperature", int.Parse(eventArgs.ApplicationMessage.ConvertPayloadToString()));
				break;
			case "authome/dht/temperature":
				await _hub.Clients.All.SendAsync("Temperature", int.Parse(eventArgs.ApplicationMessage.ConvertPayloadToString()));
				break;
			case "authome/dht/humidity":
				await _hub.Clients.All.SendAsync("Humidity", int.Parse(eventArgs.ApplicationMessage.ConvertPayloadToString()));
				break;
			case "authome/fingerprint/data":
				_imageStore.TryEncodeAndSaveAsImage(eventArgs.ApplicationMessage.Payload, out _);
				break;
			default:
				break;
		}
		

		Match match = reg.Match(eventArgs.ApplicationMessage.Topic);
		if (match.Success)
		{
			Guid userId = new(match.Groups["userId"].Value);

			using AuthomeContext ctx = new();
			var query = ctx.Users.Where(u => u.Id == userId);
			if (!query.Any())
				return;

			User u = query.Single();
			switch (match.Groups["property"].Value)
			{
				case "image":
					FingerImage? fi;
					_imageStore.TryEncodeAndSaveAsImage(eventArgs.ApplicationMessage.Payload, out fi);
					u.FingerImage = fi;
					ctx.SaveChanges();
					break;
				case "characteristics":
					u.CharacteristicsData = eventArgs.ApplicationMessage.Payload;
					ctx.SaveChanges();
					break;
				case "index":
					u.ImageIndex = ushort.Parse(Encoding.UTF8.GetString(eventArgs.ApplicationMessage.Payload));
					ctx.SaveChanges();
					break;
			}
		}
		
	}
}
