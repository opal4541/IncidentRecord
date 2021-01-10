USE [Senior2]
GO
SET IDENTITY_INSERT [dbo].[LicensePlate] ON 

INSERT [dbo].[LicensePlate] ([LicensePlateID], [LicensePlate], [EnterDate], [EnterTime]) VALUES (1, N'ฌง5289', CAST(N'2021-01-10' AS Date), CAST(N'19:39:00' AS Time))
INSERT [dbo].[LicensePlate] ([LicensePlateID], [LicensePlate], [EnterDate], [EnterTime]) VALUES (2, N'ณ8345', CAST(N'2021-01-10' AS Date), CAST(N'19:40:00' AS Time))
INSERT [dbo].[LicensePlate] ([LicensePlateID], [LicensePlate], [EnterDate], [EnterTime]) VALUES (3, N'4กด29', CAST(N'2021-01-10' AS Date), CAST(N'19:45:00' AS Time))
INSERT [dbo].[LicensePlate] ([LicensePlateID], [LicensePlate], [EnterDate], [EnterTime]) VALUES (4, N'4กต29', CAST(N'2021-01-10' AS Date), CAST(N'19:50:00' AS Time))
SET IDENTITY_INSERT [dbo].[LicensePlate] OFF
GO
SET IDENTITY_INSERT [dbo].[Blacklist] ON 

INSERT [dbo].[Blacklist] ([BlacklistID], [LicensePlateID], [Remark]) VALUES (1, 3, N'ใช้แบงค์ปลอม')
INSERT [dbo].[Blacklist] ([BlacklistID], [LicensePlateID], [Remark]) VALUES (2, 4, N'เติมน้ำมันผิด')
SET IDENTITY_INSERT [dbo].[Blacklist] OFF
GO
SET IDENTITY_INSERT [dbo].[User] ON 

INSERT [dbo].[User] ([UserID], [Username], [Password], [Firstname], [Lastname], [UserType]) VALUES (1, N'opal', N'6010017', N'Nuntanutch', N'Tharapong', N'Admin')
INSERT [dbo].[User] ([UserID], [Username], [Password], [Firstname], [Lastname], [UserType]) VALUES (2, N'pim', N'6013633', N'Kamonrut', N'Vorrawongprasert', N'Admin')
INSERT [dbo].[User] ([UserID], [Username], [Password], [Firstname], [Lastname], [UserType]) VALUES (3, N'neung', N'6010000', N'Chayapol', N'Moemeng', N'User')
SET IDENTITY_INSERT [dbo].[User] OFF
GO
