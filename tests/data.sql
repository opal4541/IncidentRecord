USE [IncidentRecord]
GO
SET IDENTITY_INSERT [dbo].[User] ON 

INSERT [dbo].[User] ([UserID], [UserName], [Password], [FirstName], [LastName], [UserType]) VALUES (1, N'Opal', N'6010017', N'Nuntanuch', N'Tharapong', N'Admin')
INSERT [dbo].[User] ([UserID], [UserName], [Password], [FirstName], [LastName], [UserType]) VALUES (2, N'Pim', N'6013633', N'Kamonrut', N'Vorrawongprasert', N'Admin')
INSERT [dbo].[User] ([UserID], [UserName], [Password], [FirstName], [LastName], [UserType]) VALUES (3, N'Nueng', N'1234567', N'Chayapol', N'Moemeng', N'User')
SET IDENTITY_INSERT [dbo].[User] OFF
GO
