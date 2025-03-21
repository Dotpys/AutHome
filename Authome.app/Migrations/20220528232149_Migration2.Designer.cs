﻿// <auto-generated />
using System;
using AutHome;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Infrastructure;
using Microsoft.EntityFrameworkCore.Migrations;
using Microsoft.EntityFrameworkCore.Storage.ValueConversion;

#nullable disable

namespace AutHome.Migrations
{
    [DbContext(typeof(AuthomeContext))]
    [Migration("20220528232149_Migration2")]
    partial class Migration2
    {
        protected override void BuildTargetModel(ModelBuilder modelBuilder)
        {
#pragma warning disable 612, 618
            modelBuilder.HasAnnotation("ProductVersion", "6.0.4");

            modelBuilder.Entity("AutHome.Data.FingerImage", b =>
                {
                    b.Property<Guid>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("TEXT");

                    b.Property<DateTime>("Timestamp")
                        .HasColumnType("TEXT");

                    b.HasKey("Id");

                    b.ToTable("Images");
                });

            modelBuilder.Entity("AutHome.Data.User", b =>
                {
                    b.Property<Guid>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("TEXT");

                    b.Property<byte[]>("CharacteristicsData")
                        .HasColumnType("BLOB");

                    b.Property<Guid?>("FingerImageId")
                        .HasColumnType("TEXT");

                    b.Property<string>("FirstName")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<string>("LastName")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<DateOnly>("RegistrationDate")
                        .HasColumnType("TEXT");

                    b.HasKey("Id");

                    b.HasIndex("FingerImageId");

                    b.ToTable("Users");
                });

            modelBuilder.Entity("AutHome.Data.User", b =>
                {
                    b.HasOne("AutHome.Data.FingerImage", "FingerImage")
                        .WithMany()
                        .HasForeignKey("FingerImageId");

                    b.Navigation("FingerImage");
                });
#pragma warning restore 612, 618
        }
    }
}
