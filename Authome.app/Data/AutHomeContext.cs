using AutHome.Data;
using Microsoft.EntityFrameworkCore;

namespace AutHome;

public class AutHomeContext : DbContext
{
	public DbSet<User> Users { get; set; }

	protected override void OnConfiguring(DbContextOptionsBuilder options)
	{
		options.UseSqlite($"Data Source=authome.db");
	}
}