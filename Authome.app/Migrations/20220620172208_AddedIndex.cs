using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace AutHome.Migrations
{
    public partial class AddedIndex : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<ushort>(
                name: "ImageIndex",
                table: "Users",
                type: "INTEGER",
                nullable: true);

            migrationBuilder.AddColumn<bool>(
                name: "AccessGranted",
                table: "AccessEntries",
                type: "INTEGER",
                nullable: false,
                defaultValue: false);
        }

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "ImageIndex",
                table: "Users");

            migrationBuilder.DropColumn(
                name: "AccessGranted",
                table: "AccessEntries");
        }
    }
}
