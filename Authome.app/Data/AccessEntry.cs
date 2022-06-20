namespace AutHome.Data;

public class AccessEntry
{
	/// <summary>
	/// The identifier of this specific entity.
	/// </summary>
	public Guid Id { get; set; }

	/// <summary>
	/// Date and Time at wich access was registered.
	/// </summary>
	public DateTime Timestamp { get; set; }

	/// <summary>
	/// Whether this access attempt was successful or not.
	/// </summary>
	public bool AccessGranted { get; set; }

	public User User { get; set; }
}
