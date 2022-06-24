using AutHome.Data;

namespace AutHome.Services;

public class UserFingerprintService
{
	private const int LIBRARY_MAX_SIZE = 150;

	private readonly AuthomeContext _authomeContext;

	public UserFingerprintService()
	{
		_authomeContext = new AuthomeContext();
	}

	~UserFingerprintService()
	{
		_authomeContext.Dispose();
	}

	public void SendUserRegistrationCommand(User user)
	{
		if (!TryFindNextFreeIndex(out ushort index))
			return;
		byte[] payloadBuffer = new byte[19];
		payloadBuffer[0] = 0x01;    //Codice comando Registrazione impronta
		string guidString = user.Id.ToString("N");
		for (int i = 0; i < 16; i++)
		{
			payloadBuffer[1 + i] = byte.Parse(guidString.Substring(i * 2, 2), System.Globalization.NumberStyles.HexNumber);
		}
		payloadBuffer[17] = (byte)((index & 0xFF00) >> 8);
		payloadBuffer[18] = (byte)((index & 0x00FF) >> 0);
		MQTTConnectionService.MqttClient.PublishAsync(
			new MQTTnet.MqttApplicationMessage()
			{
				Topic = "authome/mcu/command",
				Payload = payloadBuffer
			});
	}

	public void SendUserDeletionCommand(User user)
	{
		if (user != null && user.ImageIndex != null)
		{
			byte[] payloadBuffer = new byte[] { 0x02, (byte)(user.ImageIndex >> 8), (byte)(user.ImageIndex & 0x00FF) };
			MQTTConnectionService.MqttClient.PublishAsync(
				new MQTTnet.MqttApplicationMessage()
				{
					Topic = "authome/mcu/command",
					Payload = payloadBuffer
				});
		}
	}

	public void DeleteCharacteristicAt(ushort index)
	{
		byte[] payloadBuffer = new byte[] { 0x02, (byte)(index >> 8), (byte)(index & 0x00FF) };
		MQTTConnectionService.MqttClient.PublishAsync(
			new MQTTnet.MqttApplicationMessage()
			{
				Topic = "authome/mcu/command",
				Payload = payloadBuffer
			});
	}

	private bool TryFindNextFreeIndex(out ushort index)
	{
		var registeredUsers = _authomeContext.Users.Where(u => u.ImageIndex != null);
		for (ushort i=0; i<LIBRARY_MAX_SIZE; i++)
		{
			if (!registeredUsers.Any(u => u.ImageIndex == i))
			{
				index = i;
				return true;
			}
		}
		index = 0;
		return false;
	}
}
