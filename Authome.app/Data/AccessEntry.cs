using Microsoft.EntityFrameworkCore.Infrastructure;

namespace AutHome.Data;

public class AccessEntry
{
	private User _user;
	private ILazyLoader LazyLoader { get; set; } = null!;

	public Guid Id { get; set; }
	public DateTime Timestamp { get; set; }
	bool AccessGranted { get; set; }
	public User User
	{
		get => LazyLoader.Load(this, ref _user);
		set => _user = value;
	}

	private AccessEntry(ILazyLoader lazyLoader)
	{
		LazyLoader = lazyLoader;
	}
}
