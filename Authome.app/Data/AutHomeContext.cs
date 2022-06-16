using AutHome.Data;
using Microsoft.EntityFrameworkCore;

namespace AutHome;

public class AuthomeContext : DbContext
{
	public DbSet<User> Users { get; set; } = null!;
	public DbSet<FingerImage> Images { get; set; } = null!;

	protected override void OnConfiguring(DbContextOptionsBuilder options)
	{
		options.UseSqlite($"Data Source=authome.db");
	}
}