namespace AutHome.Data;

public class AccessEntry
{
	public Guid Id { get; set; }
	public DateTime Timestamp { get; set; }
	public User User { get; set; } = null!;
}
