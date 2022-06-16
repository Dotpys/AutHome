namespace AutHome.Data;

public class User
{
	public Guid Id { get; set; }
	public string FirstName { get; set; } = string.Empty;
	public string LastName { get; set; } = string.Empty;
	public DateOnly RegistrationDate { get; set; }
	public byte[]? CharacteristicsData { get; set; }
	public FingerImage? FingerImage { get; set; }
}