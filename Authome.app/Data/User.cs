using Microsoft.EntityFrameworkCore.Infrastructure;

namespace AutHome.Data;

public class User
{
	private FingerImage? _fingerImage;
	private ILazyLoader LazyLoader { get; set; }

	public Guid Id { get; set; }
	public string FirstName { get; set; } = string.Empty;
	public string LastName { get; set; } = string.Empty;
	public DateOnly RegistrationDate { get; set; }
	public byte[]? CharacteristicsData { get; set; }
	public FingerImage? FingerImage
	{
		get => LazyLoader.Load(this, ref _fingerImage);
		set => _fingerImage = value;
	}

	public User()
	{
	}

	private User(ILazyLoader lazyLoader)
	{
		LazyLoader = lazyLoader;
	}
}