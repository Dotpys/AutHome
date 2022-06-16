namespace AutHome.Data;

public class FingerImage
{
	public Guid Id { get; set; }
	public DateTime Timestamp { get; set; }
	public string Path { get { return $"/cdn/image/{Id:N}.png"; } }
}