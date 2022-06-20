namespace AutHome.Data;

public class User
{
	public Guid Id { get; set; }
	public string FirstName { get; set; } = null!;
	public string LastName { get; set; } = null!;
	public DateOnly RegistrationDate { get; set; }
	public byte[]? CharacteristicsData { get; set; }
	public FingerImage? FingerImage { get; set; }
	public ushort? ImageIndex { get; set; }
}