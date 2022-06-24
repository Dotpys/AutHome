using Microsoft.AspNetCore.SignalR.Client;
using Microsoft.AspNetCore.SignalR;
using AutHome.Hubs;
using MQTTnet;
using MQTTnet.Client;
using System.Text.RegularExpressions;
using AutHome.Data;
using System.Text;

namespace AutHome.Services;

public class MQTTConnectionService : IHostedService, IDisposable
{
	private readonly IConfiguration _configuration;
	private readonly ILogger<MQTTConnectionService> _logger;
	private readonly IHubContext<DashboardHub> _hubDashboard;
	private readonly IHubContext<UsersHub> _hubUsers;
	private readonly IHubContext<AccessListHub> _hubAccessList;
	private readonly FingerprintImageStore _imageStore;

	private readonly MqttFactory _mqttFactory;
	private static IMqttClient _mqttClient = null!;
	private static MqttClientOptions _mqttClientOptions = null!;
	private readonly Regex _userPropertyPattern;

	public static IMqttClient MqttClient { get => _mqttClient; }

	public static bool IsConnected { get => _mqttClient.IsConnected; }

	public static string MCUStatus { get; set; } = string.Empty;
	public static int? MCUTemperature { get; set; } = null;
	public static int? DHTTemperature { get; set; } = null;
	public static int? DHTHumidity { get; set; } = null;
	public static bool? Relay1State { get; set; } = null;
	public static bool? Relay2State { get; set; } = null;
	public static bool? Relay3State { get; set; } = null;

	public MQTTConnectionService(
		IConfiguration mqttConfiguration,
		ILogger<MQTTConnectionService> logger,
		IHubContext<DashboardHub> hubDashboard,
		IHubContext<UsersHub> hubUsers,
		IHubContext<AccessListHub> hubAccessList,
		FingerprintImageStore imageStore)
	{
		_configuration = mqttConfiguration;
		_logger = logger;
		_hubDashboard = hubDashboard;
		_hubUsers = hubUsers;
		_hubAccessList = hubAccessList;
		_imageStore = imageStore;
		_userPropertyPattern = new(@"authome\/user\/(?<userId>[0-9A-F]{32})\/(?<property>(image|characteristics|index))");

		_mqttFactory = new();
		
	}

	public async Task StartAsync(CancellationToken cancellationToken)
	{
		_mqttClient = _mqttFactory.CreateMqttClient();
		string host = _configuration.GetValue("MQTT:Broker:Address", "localhost");
		int port = _configuration.GetValue("MQTT:Broker:Port", 1883);
		_mqttClientOptions = new MqttClientOptionsBuilder()
			.WithTcpServer(host, port)
			.WithClientId(_configuration.GetValue("MQTT:ClientId", "Backend-Client"))
			.Build();
		MqttClientConnectResult connectionResult = await _mqttClient.ConnectAsync(_mqttClientOptions, cancellationToken);
		_logger.LogInformation("Connected to MQTT broker.");
		await _mqttClient.SubscribeAsync("authome/#", cancellationToken: cancellationToken);
		_mqttClient.ApplicationMessageReceivedAsync += MessageReceived;
	}

	public async Task StopAsync(CancellationToken cancellationToken)
	{
		await _mqttClient!.DisconnectAsync(new() { Reason= MqttClientDisconnectReason.NormalDisconnection}, cancellationToken);
		_logger.LogInformation("Disconnected from MQTT broker.");
	}

	public void Dispose()
	{
		GC.SuppressFinalize(this);
	}

	private async Task MessageReceived(MqttApplicationMessageReceivedEventArgs eventArgs)
	{
		switch (eventArgs.ApplicationMessage.Topic)
		{
			case "authome/mcu/status":
				MCUStatus = eventArgs.ApplicationMessage.ConvertPayloadToString();
				await _hubDashboard.Clients.All.SendAsync("MCUStatus", MCUStatus);
				break;
			case "authome/mcu/temperature":
				MCUTemperature = int.Parse(eventArgs.ApplicationMessage.ConvertPayloadToString());
				await _hubDashboard.Clients.All.SendAsync("MCUTemperature", MCUTemperature);
				break;
			case "authome/dht/temperature":
				DHTTemperature = int.Parse(eventArgs.ApplicationMessage.ConvertPayloadToString());
				await _hubDashboard.Clients.All.SendAsync("DHTTemperature", DHTTemperature);
				break;
			case "authome/dht/humidity":
				DHTHumidity = int.Parse(eventArgs.ApplicationMessage.ConvertPayloadToString());
				await _hubDashboard.Clients.All.SendAsync("DHTHumidity", DHTHumidity);
				break;
			case "authome/relay/1":
				Relay1State = eventArgs.ApplicationMessage.Payload[0] == 0x01;
				await _hubDashboard.Clients.All.SendAsync("Relay1State", Relay1State);
				break;
			case "authome/relay/2":
				Relay2State = eventArgs.ApplicationMessage.Payload[0] == 0x01;
				await _hubDashboard.Clients.All.SendAsync("Relay2State", Relay2State);
				break;
			case "authome/relay/3":
				Relay3State = eventArgs.ApplicationMessage.Payload[0] == 0x01;
				await _hubDashboard.Clients.All.SendAsync("Relay3State", Relay3State);
				break;


			case "authome/fingerprint/data":
				_imageStore.TryEncodeAndSaveAsImage(eventArgs.ApplicationMessage.Payload, out _);
				break;
			case "authome/access":
				ushort index = ushort.Parse(eventArgs.ApplicationMessage.ConvertPayloadToString());
				using (AuthomeContext ctx = new())
				{
					User u = ctx.Users.Single(u => u.ImageIndex == index);
					ctx.AccessEntries.Add(
						new AccessEntry()
						{
							Id = Guid.NewGuid(),
							Timestamp = DateTime.UtcNow,
							User = u
						});
					ctx.SaveChanges();
					await _hubAccessList.Clients.All.SendAsync("Update");
				}
				break;
			default:
				break;
		}
		

		Match match = _userPropertyPattern.Match(eventArgs.ApplicationMessage.Topic);
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
					await _hubUsers.Clients.All.SendAsync("Update");
					break;
			}
		}
		
	}
}
