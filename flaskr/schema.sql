USE [master]
GO
/****** Object:  Database [IncidentRecord]    Script Date: 1/25/2021 3:21:26 AM ******/
CREATE DATABASE [IncidentRecord]
 CONTAINMENT = NONE
 ON  PRIMARY 
( NAME = N'IncidentRecord', FILENAME = N'D:\SqlData\IncidentRecord.mdf' , SIZE = 8192KB , MAXSIZE = UNLIMITED, FILEGROWTH = 65536KB )
 LOG ON 
( NAME = N'IncidentRecord_log', FILENAME = N'D:\SqlData\IncidentRecord_log.ldf' , SIZE = 8192KB , MAXSIZE = 2048GB , FILEGROWTH = 65536KB )
 WITH CATALOG_COLLATION = DATABASE_DEFAULT
GO
ALTER DATABASE [IncidentRecord] SET COMPATIBILITY_LEVEL = 150
GO
IF (1 = FULLTEXTSERVICEPROPERTY('IsFullTextInstalled'))
begin
EXEC [IncidentRecord].[dbo].[sp_fulltext_database] @action = 'enable'
end
GO
ALTER DATABASE [IncidentRecord] SET ANSI_NULL_DEFAULT OFF 
GO
ALTER DATABASE [IncidentRecord] SET ANSI_NULLS OFF 
GO
ALTER DATABASE [IncidentRecord] SET ANSI_PADDING OFF 
GO
ALTER DATABASE [IncidentRecord] SET ANSI_WARNINGS OFF 
GO
ALTER DATABASE [IncidentRecord] SET ARITHABORT OFF 
GO
ALTER DATABASE [IncidentRecord] SET AUTO_CLOSE OFF 
GO
ALTER DATABASE [IncidentRecord] SET AUTO_SHRINK OFF 
GO
ALTER DATABASE [IncidentRecord] SET AUTO_UPDATE_STATISTICS ON 
GO
ALTER DATABASE [IncidentRecord] SET CURSOR_CLOSE_ON_COMMIT OFF 
GO
ALTER DATABASE [IncidentRecord] SET CURSOR_DEFAULT  GLOBAL 
GO
ALTER DATABASE [IncidentRecord] SET CONCAT_NULL_YIELDS_NULL OFF 
GO
ALTER DATABASE [IncidentRecord] SET NUMERIC_ROUNDABORT OFF 
GO
ALTER DATABASE [IncidentRecord] SET QUOTED_IDENTIFIER OFF 
GO
ALTER DATABASE [IncidentRecord] SET RECURSIVE_TRIGGERS OFF 
GO
ALTER DATABASE [IncidentRecord] SET  DISABLE_BROKER 
GO
ALTER DATABASE [IncidentRecord] SET AUTO_UPDATE_STATISTICS_ASYNC OFF 
GO
ALTER DATABASE [IncidentRecord] SET DATE_CORRELATION_OPTIMIZATION OFF 
GO
ALTER DATABASE [IncidentRecord] SET TRUSTWORTHY OFF 
GO
ALTER DATABASE [IncidentRecord] SET ALLOW_SNAPSHOT_ISOLATION OFF 
GO
ALTER DATABASE [IncidentRecord] SET PARAMETERIZATION SIMPLE 
GO
ALTER DATABASE [IncidentRecord] SET READ_COMMITTED_SNAPSHOT OFF 
GO
ALTER DATABASE [IncidentRecord] SET HONOR_BROKER_PRIORITY OFF 
GO
ALTER DATABASE [IncidentRecord] SET RECOVERY FULL 
GO
ALTER DATABASE [IncidentRecord] SET  MULTI_USER 
GO
ALTER DATABASE [IncidentRecord] SET PAGE_VERIFY CHECKSUM  
GO
ALTER DATABASE [IncidentRecord] SET DB_CHAINING OFF 
GO
ALTER DATABASE [IncidentRecord] SET FILESTREAM( NON_TRANSACTED_ACCESS = OFF ) 
GO
ALTER DATABASE [IncidentRecord] SET TARGET_RECOVERY_TIME = 60 SECONDS 
GO
ALTER DATABASE [IncidentRecord] SET DELAYED_DURABILITY = DISABLED 
GO
ALTER DATABASE [IncidentRecord] SET ACCELERATED_DATABASE_RECOVERY = OFF  
GO
EXEC sys.sp_db_vardecimal_storage_format N'IncidentRecord', N'ON'
GO
ALTER DATABASE [IncidentRecord] SET QUERY_STORE = OFF
GO
USE [IncidentRecord]
GO
/****** Object:  Table [dbo].[Car]    Script Date: 1/25/2021 3:21:27 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Car](
	[CarID] [int] IDENTITY(1,1) NOT NULL,
	[CustomerID] [int] NOT NULL,
	[LicensePlate] [nvarchar](10) NOT NULL,
 CONSTRAINT [PK_Car] PRIMARY KEY CLUSTERED 
(
	[CarID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
 CONSTRAINT [UK_LicensePlate] UNIQUE NONCLUSTERED 
(
	[LicensePlate] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Customer]    Script Date: 1/25/2021 3:21:27 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Customer](
	[CustomerID] [int] IDENTITY(1,1) NOT NULL,
	[FirstName] [nvarchar](50) NULL,
	[LastName] [nvarchar](50) NULL,
	[Phone] [nvarchar](10) NULL,
 CONSTRAINT [PK_Customer] PRIMARY KEY CLUSTERED 
(
	[CustomerID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[History]    Script Date: 1/25/2021 3:21:27 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[History](
	[HistoryID] [int] IDENTITY(1,1) NOT NULL,
	[CarID] [int] NOT NULL,
	[EnterTimestamp] [datetime] NOT NULL,
	[ExitTimestamp] [datetime] NULL,
	[Activity] [nvarchar](500) NULL,
 CONSTRAINT [PK_History] PRIMARY KEY CLUSTERED 
(
	[HistoryID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Incident]    Script Date: 1/25/2021 3:21:27 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Incident](
	[IncidentID] [int] IDENTITY(1,1) NOT NULL,
	[CarID] [int] NOT NULL,
	[UserID] [int] NOT NULL,
	[Description] [nvarchar](1000) NOT NULL,
	[Type] [nvarchar](10) NOT NULL,
	[StartTimestamp] [datetime] NOT NULL,
	[EndTimestamp] [datetime] NULL,
	[Status] [nvarchar](10) NOT NULL,
 CONSTRAINT [PK_Incident] PRIMARY KEY CLUSTERED 
(
	[IncidentID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[User]    Script Date: 1/25/2021 3:21:27 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[User](
	[UserID] [int] IDENTITY(1,1) NOT NULL,
	[UserName] [nvarchar](50) NOT NULL,
	[Password] [nvarchar](30) NOT NULL,
	[FirstName] [nvarchar](50) NOT NULL,
	[LastName] [nvarchar](50) NOT NULL,
	[UserType] [nvarchar](10) NOT NULL,
 CONSTRAINT [PK_User] PRIMARY KEY CLUSTERED 
(
	[UserID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
 CONSTRAINT [UK_UserName] UNIQUE NONCLUSTERED 
(
	[UserName] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
ALTER TABLE [dbo].[Car]  WITH CHECK ADD  CONSTRAINT [FK_Car_Customer] FOREIGN KEY([CustomerID])
REFERENCES [dbo].[Customer] ([CustomerID])
GO
ALTER TABLE [dbo].[Car] CHECK CONSTRAINT [FK_Car_Customer]
GO
ALTER TABLE [dbo].[History]  WITH CHECK ADD  CONSTRAINT [FK_History_Car] FOREIGN KEY([CarID])
REFERENCES [dbo].[Car] ([CarID])
GO
ALTER TABLE [dbo].[History] CHECK CONSTRAINT [FK_History_Car]
GO
ALTER TABLE [dbo].[Incident]  WITH CHECK ADD  CONSTRAINT [FK_Incident_Car] FOREIGN KEY([CarID])
REFERENCES [dbo].[Car] ([CarID])
GO
ALTER TABLE [dbo].[Incident] CHECK CONSTRAINT [FK_Incident_Car]
GO
ALTER TABLE [dbo].[Incident]  WITH CHECK ADD  CONSTRAINT [FK_Incident_User] FOREIGN KEY([UserID])
REFERENCES [dbo].[User] ([UserID])
GO
ALTER TABLE [dbo].[Incident] CHECK CONSTRAINT [FK_Incident_User]
GO
USE [master]
GO
ALTER DATABASE [IncidentRecord] SET  READ_WRITE 
GO
